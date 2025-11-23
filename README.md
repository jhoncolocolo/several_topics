arreglo pc

## 🔒 Resumen del Problema de Permisos en IBM MQ (Windows)

El inconveniente se debe a un conflicto estándar entre los requisitos de **Administración de Sistemas de Windows** y la **Autorización de IBM MQ**.

### 💡 Análisis de la Raíz del Problema

El instalador de IBM MQ, ejecutado por el administrador, crea recursos a **nivel de sistema** (servicios, archivos protegidos) y establece el grupo de seguridad local **`mqm`**.

| Componente | Causa del Problema | Requisito de Seguridad (Solución) |
| :--- | :--- | :--- |
| **Instalación/Visibilidad** | El instalador (MSI) requiere **privilegios de Administrador** para elevar el proceso (UAC) y modificar el sistema. | Ejecución elevada **obligatoria** para el *setup*. |
| **Operación (`crtmqm`, comandos)** | El usuario estándar no es miembro del grupo **`mqm`**, que es el *Access Control Group* (ACG) de IBM MQ. | El usuario debe ser miembro del grupo **`mqm`**. |
| **Error "Acceso Denegado"** | El intento de agregar el usuario a **`mqm`** fue realizado por una cuenta que **no tenía derechos de Administrador Local** en la máquina. | La modificación de grupos locales requiere **Administrador Local** en el host. |
| **Conexión de Aplicaciones** | El gestor de colas (QMGR) realiza una comprobación de autorización del sistema operativo, y el usuario no tiene permisos de conexión/acceso a la cola. | **Autorización granular de MQ** (`setmqaut`) o uso de `MCAUSER` en el canal SVRCONN. |

---

## ✅ Soluciones Estratégicas (Enfocadas en Seguridad)

La solución consiste en delegar la autoridad operativa a los usuarios sin comprometer la cuenta de administrador.

### 1. Solución Principal y Obligatoria (Sistema Operativo)

**Acción:** Agregar al usuario estándar al grupo **`mqm`**.

* **Requisito de Seguridad:** Esta acción **debe ser ejecutada** por un usuario que posea credenciales de **Administrador Local** en el host de MQ.
* **Procedimiento:**
    1.  Iniciar sesión con credenciales de Administrador Local.
    2.  Usar la herramienta de administración de usuarios (ej: `lusrmgr.msc` o `net localgroup`).
    3.  Ejecutar el comando de forma segura (ejecutado como administrador):
        ```bash
        net localgroup mqm "DOMINIO\NombreDeUsuario" /add
        ```
    4.  El usuario debe **reiniciar su sesión** para que los nuevos permisos de grupo sean efectivos.

### 2. Solución de Autorización Granular (IBM MQ)

Si el paso 1 no es suficiente o si la política requiere menos permisos:

* **Usar `setmqaut`:** El administrador de MQ debe usar el comando `setmqaut` para otorgar solo los permisos funcionales mínimos (ej: `+connect`, `+put`, `+get`) a la cola/gestor de colas específico, en lugar de dar toda la autoridad de `mqm`.
    ```bash
    setmqaut -m QMGR_TEST -t qmgr -p UsuarioMQ +connect +inq
    `

################################################################################################
```python
# tests/test_procesador.py
import sys
import types
import json
import base64
import pytest
from unittest.mock import Mock

# ------------------------------------------------------------
# IMPORT SAFETY: inyectamos un stub para services.openfga_sync_retry_hander
# para evitar ejecutar el código que crea boto3/botocore.Config durante la importación.
# ------------------------------------------------------------
stub_module_name = "services.openfga_sync_retry_hander"
if stub_module_name not in sys.modules:
    stub = types.ModuleType(stub_module_name)
    def enviar_registro_a_reintento_o_dlq(registro, es_dlq=False):
        # no hace nada; será parcheada en tests cuando se necesite inspección
        return None
    stub.enviar_registro_a_reintento_o_dlq = enviar_registro_a_reintento_o_dlq
    sys.modules[stub_module_name] = stub

# Ahora importamos el módulo bajo prueba SIN que se ejecute el openfga_sync_retry_hander real.
import importlib
procesador_module = importlib.import_module("services.procesador")

# Importamos excepciones reales (si existen)
from services.excepciones import (
    BadRequestError,
    RedisError,
    TransientError,
    OpenFGAError
)

# ============================================================
# HELPERS COMUNES
# ============================================================

BASE_EVENT = {
    "antigua_data_usr": {"string": "my_usr"},
    "antigua_data_num": {"string": "B_0000001"},
    "antigua_data_tipo": {"string": "G"},
    "antigua_fuente": {"string": "TABLA1"},
    "data_usr": {"string": "my_usr"},
    "data_num": {"string": "B_0000001"},
    "data_tipo": {"string": "S"},
    "fuente": {"string": "TABLA1"},
    "EVENTO_TIPO": {"string": "EL"},
    "ARG_TIMESTAMP": {"string": "2025-11-20 15:16:25.369782"}
}

# --- MSK helpers ---
def msk_record_from_payload(payload, offset=None):
    value = base64.b64encode(json.dumps(payload).encode()).decode()
    rec = {"value": value}
    if offset is not None:
        rec["offset"] = offset
    return rec

def make_msk_event(payloads_by_topic_partition):
    """
    payloads_by_topic_partition: dict keyed by 'topic-partition' -> list of payload dicts
    Example: {"miTopic-1": [p1, p2, p3], "miTopic-2": [p4,p5]}
    """
    records = {}
    for tp, plist in payloads_by_topic_partition.items():
        recs = []
        base_off = 100
        for i, p in enumerate(plist):
            recs.append(msk_record_from_payload(p, offset=base_off + i))
        records[tp] = recs
    return {"fuenteEvento": "aws:kafka", "records": records}

# --- SQS helpers ---
def make_sqs_event_batch(list_of_payloads, retries_list=None):
    if retries_list is None:
        retries_list = ["1"] * len(list_of_payloads)

    records = []
    for i, payload in enumerate(list_of_payloads):
        body = json.dumps({"openfgaOperations": [payload]})
        records.append({
            "fuenteEvento": "aws:sqs",
            "messageId": f"id-{i+1}",
            "body": body,
            "attributes": {"ApproximateReceiveCount": retries_list[i]}
        })
    return {"Records": records}

# ============================================================
# Dummy Redis (simple) y SharedDummyRedis secuencial
# ============================================================

class DummyRedis:
    def __init__(self, behavior):
        self.behavior = behavior

    def save_event(self, event, fuente, tipo):
        result = self.behavior.get("save_event")
        if isinstance(result, Exception):
            raise result
        return result

class SharedDummyRedis:
    """
    Secuencial: consume una lista de valores/excepciones por each save_event call.
    """
    def __init__(self, values):
        self.values = list(values)

    def save_event(self, event, fuente, tipo):
        if not self.values:
            return 1
        v = self.values.pop(0)
        if isinstance(v, Exception):
            raise v
        return v

# ============================================================
# FIXTURE GLOBAL: parchea ServicioRedis, obtener_evento_identificador, procesar_evento, enviar_registro...
# ============================================================

@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    # Redis por defecto que acepta eventos (1)
    def redis_accept_factory():
        return DummyRedis({"save_event": 1})

    monkeypatch.setattr(procesador_module, "ServicioRedis", lambda: redis_accept_factory())

    # obtener_evento_identificador -> devuelve valores validos
    monkeypatch.setattr(procesador_module, "obtener_evento_identificador", lambda ev: {"fuente": "TABLA1", "tipo": "AC"})

    # procesar_evento mockeado por defecto
    mocked_procesar_evento = Mock()
    monkeypatch.setattr(procesador_module, "procesar_evento", mocked_procesar_evento)

    # enviar_registro_a_reintento_o_dlq mockeado por defecto
    mocked_retry_dlq = Mock()
    monkeypatch.setattr(procesador_module, "enviar_registro_a_reintento_o_dlq", mocked_retry_dlq)

    return {"mocked_procesar_evento": mocked_procesar_evento, "mocked_enviar_retry_dlq": mocked_retry_dlq, "monkeypatch": monkeypatch}


# ============================================================
# UTIL: instalar SharedDummyRedis y opcional side_effect para procesar_evento
# ============================================================

def install_shared_redis_and_processor(monkeypatch, save_seq, procesar_side_effect=None):
    shared = SharedDummyRedis(save_seq)
    monkeypatch.setattr(procesador_module, "ServicioRedis", lambda: shared)

    if procesar_side_effect is None:
        monkeypatch.setattr(procesador_module, "procesar_evento", Mock())
    elif isinstance(procesar_side_effect, Exception):
        def raise_all(evt, f, t):
            raise procesar_side_effect
        monkeypatch.setattr(procesador_module, "procesar_evento", raise_all)
    else:
        monkeypatch.setattr(procesador_module, "procesar_evento", procesar_side_effect)

    return shared

# ============================================================
# 8 TESTS CLÁSICOS
# ============================================================

def test_msk_success(patch_env):
    event = make_msk_event({"miTopic-1": [BASE_EVENT]})
    result = procesador_module.process_message(event)
    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()
    assert result["itemsProcesados"] == 1
    assert result["itemsFallidos"] == 0

def test_sqs_success_first_time(patch_env):
    event = make_sqs_event_batch([BASE_EVENT], retries_list=["1"])
    result = procesador_module.process_message(event)
    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()
    assert result["itemsProcesados"] == 1

def test_sqs_success_second_time(patch_env):
    event = make_sqs_event_batch([BASE_EVENT], retries_list=["2"])
    result = procesador_module.process_message(event)
    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()
    assert result["itemsProcesados"] == 1

def test_openfga_badrequest_goes_to_dlq(patch_env):
    patch_env["mocked_procesar_evento"].side_effect = BadRequestError("bad req")
    event = make_sqs_event_batch([BASE_EVENT])
    result = procesador_module.process_message(event)
    patch_env["mocked_enviar_retry_dlq"].assert_called_once()
    _, kwargs = patch_env["mocked_enviar_retry_dlq"].call_args
    assert kwargs.get("es_dlq") is True
    assert result["itemsFallidos"] == 1

def test_redis_error_sends_retry(patch_env):
    def redis_raise_factory():
        return DummyRedis({"save_event": RedisError("redis down")})
    patch_env["monkeypatch"].setattr(procesador_module, "ServicioRedis", lambda: redis_raise_factory())
    event = make_sqs_event_batch([BASE_EVENT])
    result = procesador_module.process_message(event)
    patch_env["mocked_enviar_retry_dlq"].assert_called_once()
    _, kwargs = patch_env["mocked_enviar_retry_dlq"].call_args
    assert kwargs.get("es_dlq") is False
    assert result["itemsFallidos"] == 1

def test_unexpected_exception_goes_retry(patch_env):
    patch_env["mocked_procesar_evento"].side_effect = Exception("boom")
    event = make_sqs_event_batch([BASE_EVENT])
    result = procesador_module.process_message(event)
    patch_env["mocked_enviar_retry_dlq"].assert_called_once()
    _, kwargs = patch_env["mocked_enviar_retry_dlq"].call_args
    assert kwargs.get("es_dlq") is False
    assert result["itemsFallidos"] == 1

def test_redis_save_event_return_zero_ignores(patch_env):
    def redis_zero_factory():
        return DummyRedis({"save_event": 0})
    patch_env["monkeypatch"].setattr(procesador_module, "ServicioRedis", lambda: redis_zero_factory())
    event = make_sqs_event_batch([BASE_EVENT])
    result = procesador_module.process_message(event)
    patch_env["mocked_procesar_evento"].assert_not_called()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()
    assert result["itemsProcesados"] == 0 and result["itemsFallidos"] == 0

def test_redis_more_recent_event_ignores_sqs_retry(patch_env):
    def redis_zero_factory():
        return DummyRedis({"save_event": 0})
    patch_env["monkeypatch"].setattr(procesador_module, "ServicioRedis", lambda: redis_zero_factory())
    event = make_sqs_event_batch([BASE_EVENT], retries_list=["3"])
    result = procesador_module.process_message(event)
    patch_env["mocked_procesar_evento"].assert_not_called()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()
    assert result["itemsProcesados"] == 0 and result["itemsFallidos"] == 0

# ============================================================
# 4 TESTS DE BITÁCORA
# ============================================================

def test_msk_batch_log(patch_env):
    event = make_msk_event({"miTopic-1": [BASE_EVENT, BASE_EVENT, BASE_EVENT]})
    result = procesador_module.process_message(event)
    assert result["origen"] == "MSK"
    assert result["itemsProcesados"] == 3
    assert result["itemsFallidos"] == 0
    assert len(result["itemExitososBatch"]) == 3

def test_sqs_batch_log(patch_env):
    event = make_sqs_event_batch([BASE_EVENT, BASE_EVENT], retries_list=["2","1"])
    result = procesador_module.process_message(event)
    assert result["origen"] == "SQS"
    assert result["itemsProcesados"] == 2
    assert result["itemExitososBatch"][0]["numeroReintento"] == "2"

def test_batch_log_badrequest(patch_env):
    patch_env["mocked_procesar_evento"].side_effect = BadRequestError("bad req")
    event = make_sqs_event_batch([BASE_EVENT])
    result = procesador_module.process_message(event)
    assert result["itemsFallidos"] == 1
    assert result["itemFallidosBatch"][0]["destino"] == "DLQ"

def test_batch_log_retry_transient_error(patch_env):
    patch_env["mocked_procesar_evento"].side_effect = TransientError("temp")
    event = make_sqs_event_batch([BASE_EVENT])
    result = procesador_module.process_message(event)
    assert result["itemsFallidos"] == 1
    assert result["itemFallidosBatch"][0]["destino"] == "RETRY"

# ============================================================
# 4 TESTS MSK - MULTIPLES REGISTROS (3 cada uno)
# ============================================================

def test_msk_batch_case_A_success_fail_success(patch_env):
    # 1 success, 2 badrequest -> DLQ, 3 success
    p1 = dict(BASE_EVENT)
    p2 = dict(BASE_EVENT); p2["_mark_badrequest"] = True
    p3 = dict(BASE_EVENT)
    event = make_msk_event({"miTopic-1": [p1, p2, p3]})

    def procesar_side(evt, fuente, tipo):
        if evt.get("_mark_badrequest"):
            raise BadRequestError("bad")
        return None

    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,1], procesar_side_effect=procesar_side)
    result = procesador_module.process_message(event)

    assert result["itemsProcesados"] == 2
    assert result["itemsFallidos"] == 1
    calls = patch_env["mocked_enviar_retry_dlq"].call_args_list
    assert len(calls) == 1
    _, kwargs = calls[0]
    assert kwargs.get("es_dlq") is True
    # exitosos ids contain prefix 'miTopic-1'
    assert any(str(s["itemIdentificador"]).startswith("miTopic-1") for s in result["itemExitososBatch"])

def test_msk_batch_case_B_success_fail_ignored(patch_env):
    # 1 success, 2 badrequest, 3 ignored (save_event=0)
    p1 = dict(BASE_EVENT)
    p2 = dict(BASE_EVENT); p2["_mark_badrequest"] = True
    p3 = dict(BASE_EVENT)
    event = make_msk_event({"miTopic-1": [p1, p2, p3]})

    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,0],
                                      procesar_side_effect=lambda evt, f, t: (_ for _ in ()).throw(BadRequestError("bad")) if evt.get("_mark_badrequest") else None)
    result = procesador_module.process_message(event)

    assert result["itemsProcesados"] == 1
    assert result["itemsFallidos"] == 1
    assert len(result["itemExitososBatch"]) == 1
    assert len(result["itemFallidosBatch"]) == 1

def test_msk_batch_case_C_all_success(patch_env):
    event = make_msk_event({"miTopic-1": [BASE_EVENT, BASE_EVENT, BASE_EVENT]})
    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,1], procesar_side_effect=None)
    result = procesador_module.process_message(event)
    assert result["itemsProcesados"] == 3
    assert result["itemsFallidos"] == 0
    assert len(result["itemExitososBatch"]) == 3

def test_msk_batch_case_D_all_fail(patch_env):
    event = make_msk_event({"miTopic-1": [BASE_EVENT, BASE_EVENT, BASE_EVENT]})
    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,1],
                                      procesar_side_effect=lambda evt, f, t: (_ for _ in ()).throw(TransientError("temp")))
    result = procesador_module.process_message(event)
    assert result["itemsProcesados"] == 0
    assert result["itemsFallidos"] == 3
    calls = patch_env["mocked_enviar_retry_dlq"].call_args_list
    assert len(calls) == 3
    for _, kw in calls:
        assert kw.get("es_dlq") is False

# ============================================================
# 4 TESTS SQS - MULTIPLES REGISTROS (3 cada uno)
# ============================================================

def test_sqs_batch_case_A_success_fail_success(patch_env):
    p1 = dict(BASE_EVENT)
    p2 = dict(BASE_EVENT); p2["_mark_badrequest"] = True
    p3 = dict(BASE_EVENT)
    event = make_sqs_event_batch([p1, p2, p3], retries_list=["1","1","1"])

    def procesar_side(evt, fuente, tipo):
        if evt.get("_mark_badrequest"):
            raise BadRequestError("bad")
        return None

    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,1], procesar_side_effect=procesar_side)
    result = procesador_module.process_message(event)

    assert result["itemsProcesados"] == 2
    assert result["itemsFallidos"] == 1
    calls = patch_env["mocked_enviar_retry_dlq"].call_args_list
    assert len(calls) == 1
    _, kw = calls[0]
    assert kw.get("es_dlq") is True
    assert any(it["itemIdentificador"] in ("id-1","id-3") for it in result["itemExitososBatch"])

def test_sqs_batch_case_B_success_fail_ignored(patch_env):
    p1 = dict(BASE_EVENT)
    p2 = dict(BASE_EVENT); p2["_mark_badrequest"] = True
    p3 = dict(BASE_EVENT)
    event = make_sqs_event_batch([p1, p2, p3], retries_list=["1","1","1"])

    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,0],
                                      procesar_side_effect=lambda evt, f, t: (_ for _ in ()).throw(BadRequestError("bad")) if evt.get("_mark_badrequest") else None)
    result = procesador_module.process_message(event)

    assert result["itemsProcesados"] == 1
    assert result["itemsFallidos"] == 1
    assert len(result["itemExitososBatch"]) == 1
    assert len(result["itemFallidosBatch"]) == 1

def test_sqs_batch_case_C_all_success(patch_env):
    event = make_sqs_event_batch([BASE_EVENT, BASE_EVENT, BASE_EVENT], retries_list=["1","1","1"])
    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,1], procesar_side_effect=None)
    result = procesador_module.process_message(event)
    assert result["itemsProcesados"] == 3
    assert result["itemsFallidos"] == 0
    assert len(result["itemExitososBatch"]) == 3

def test_sqs_batch_case_D_all_fail(patch_env):
    event = make_sqs_event_batch([BASE_EVENT, BASE_EVENT, BASE_EVENT], retries_list=["2","2","2"])
    install_shared_redis_and_processor(patch_env["monkeypatch"], save_seq=[1,1,1],
                                      procesar_side_effect=lambda evt, f, t: (_ for _ in ()).throw(TransientError("temp")))
    result = procesador_module.process_message(event)
    assert result["itemsProcesados"] == 0
    assert result["itemsFallidos"] == 3
    calls = patch_env["mocked_enviar_retry_dlq"].call_args_list
    assert len(calls) == 3
    for _, kw in calls:
        assert kw.get("es_dlq") is False

# \src\services\procesador.py

from services.servicio_redis import ServicioRedis
import logging
import base64
import json
from utilitarios.funcion_evento import obtener_evento_identificador, procesar_evento
from services.excepciones import (
    BadRequestError,
    RedisError,
    TransientError,
    OpenFGAError
)
from services.openfga_sync_retry_hander import enviar_registro_a_reintento_o_dlq

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# --------------------------------------------------------------------
#   CLASIFICACIÓN DE EVENTOS
# --------------------------------------------------------------------

def process_message(event):
    """
    Punto de entrada: detecta tipo MSK o SQS y delega.
    Ahora cada batch genera bitácora.
    """
    if es_evento_kafka(event):
        return proceso_kafka_evento(event)

    elif es_evento_sqs(event):
        return proceso_sqs_evento(event)

    else:
        logger.error("Origen de evento no reconocido")
        raise ValueError("Origen de evento no reconocido")


def es_evento_kafka(event):
    return 'fuenteEvento' in event and event['fuenteEvento'] == 'aws:kafka'


def es_evento_sqs(event):
    return 'Records' in event and event['Records'] and event['Records'][0].get('fuenteEvento') == 'aws:sqs'


# --------------------------------------------------------------------
#   PROCESAMIENTO KAFKA
# --------------------------------------------------------------------

def proceso_kafka_evento(event):
    """
    Procesa un batch MSK.
    Extrae múltiples records, asigna offset como messageId
    y genera bitácora completa.
    """
    batch_log = crear_batch_log(origen="MSK")

    records = event.get("records", {})

    for partition, rec_list in records.items():
        for idx, record in enumerate(rec_list):

            payload_dict = construir_evento_payload(record)
            if not payload_dict:
                continue

            # Offset como messageId (Kafka no lo entrega, pero podemos simular)
            payload_dict["messageId"] = f"{partition}:{idx}"
            payload_dict["retry"] = 0

            process_with_log(payload_dict, batch_log)

    logger.info("MSK Batch Log: " + json.dumps(batch_log))
    return batch_log


# --------------------------------------------------------------------
#   PROCESAMIENTO SQS
# --------------------------------------------------------------------

def proceso_sqs_evento(event):
    """
    Procesa batch SQS.
    """
    sqs_records = event["Records"]

    batch_log = crear_batch_log(origen="SQS")

    listado_registros = procesar_sqs_registros(sqs_records)

    for record in listado_registros:
        process_with_log(record, batch_log)

    logger.info("SQS Batch Log: " + json.dumps(batch_log))
    return batch_log


# --------------------------------------------------------------------
#   DECODIFICACIONES
# --------------------------------------------------------------------

def construir_evento_payload(record):
    """
    Decodifica payload Base64 de MSK.
    """
    try:
        payload = base64.b64decode(record['value']).decode('utf-8')
        return json.loads(payload)
    except Exception as e:
        logger.error(f"Error decodificando payload MSK: {e}")
        return None


def procesar_sqs_registros(sqs_records):
    """
    Convierte registros SQS en estructuras procesables.
    """
    listado_registros = []

    for record in sqs_records:
        body_str = record.get('body')
        body = json.loads(body_str)

        registro = body["openfgaOperations"][0]
        registro["messageId"] = record.get("messageId")
        registro["retry"] = record["attributes"].get("ApproximateReceiveCount", "1")

        listado_registros.append(registro)

    return listado_registros


# --------------------------------------------------------------------
#   PROCESO INDIVIDUAL CON BITÁCORA (NUEVO)
# --------------------------------------------------------------------

def process_with_log(event, batch_log):
    """
    Ejecuta process() y actualiza bitácora.
    Este es el ÚNICO lugar responsable de DLQ/Retry.
    """
    try:
        result = process(event)

        if result is None:
            # idempotencia: Redis dijo que ya fue procesado
            logger.info(f"Evento ignorado (idempotencia): {event.get('messageId')}")
            return

        # ÉXITO
        batch_log["itemsProcesados"] += 1
        batch_log["itemExitososBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry")
        })

    except BadRequestError:
        # Error NO reintentable ─→ DLQ
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry"),
            "error": "BadRequestError",
            "destino": "DLQ"
        })
        enviar_registro_a_reintento_o_dlq(event, es_dlq=True)

    except (RedisError, OpenFGAError, TransientError) as e:
        # Error reintentable ─→ Retry
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry"),
            "error": e.__class__.__name__,
            "destino": "RETRY"
        })
        enviar_registro_a_reintento_o_dlq(event, es_dlq=False)

    except Exception as e:
        # Error inesperado ─→ Retry
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry"),
            "error": "UnexpectedError",
            "destino": "RETRY",
            "message": str(e)
        })
        enviar_registro_a_reintento_o_dlq(event, es_dlq=False)


# --------------------------------------------------------------------
#   PROCESO INDIVIDUAL ORIGINAL — 100% SIN CAMBIAR LA LÓGICA
# --------------------------------------------------------------------

def process(event):
    """
    Realiza la lógica interna:
    - idempotencia Redis
    - procesamiento OpenFGA
    IMPORTANTE:
    Ya NO atrapa errores. Los propaga a process_with_log().
    """
    redis = ServicioRedis()
    event_identifier = obtener_evento_identificador(event)

    new_event = redis.save_event(event, event_identifier["fuente"], event_identifier["tipo"])

    if not new_event:
        return None

    procesar_evento(event, event_identifier["fuente"], event_identifier["tipo"])
    return True


# --------------------------------------------------------------------
#   UTILIDADES
# --------------------------------------------------------------------

def crear_batch_log(origen):
    return {
        "origen": origen,
        "itemsProcesados": 0,
        "itemsFallidos": 0,
        "itemExitososBatch": [],
        "itemFallidosBatch": []
    }

# tests/test_openfga_retry_handler_moto.py

import json
import boto3
from moto import mock_aws
import services.openfga_sync_retry_hander as handler


@mock_aws
def test_retry_message_integration(monkeypatch):
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = sqs.create_queue(QueueName="retry")["QueueUrl"]

    monkeypatch.setenv("RETRY_QUEUE_URL", "/retry")
    monkeypatch.setenv("DLQ_QUEUE_URL", "/dlq")
    monkeypatch.setenv("SQS_URL_ENDPOINT", queue_url.replace("/retry", ""))

    handler.sqs = boto3.client("sqs", region_name="us-east-1")

    registro = {"id": 1}
    handler.enviar_registro_a_reintento_o_dlq(registro, es_dlq=False)

    msgs = sqs.receive_message(QueueUrl=queue_url)["Messages"]
    assert len(msgs) == 1

    body = json.loads(msgs[0]["Body"])
    assert body == {"OperacionesOpenFga": [registro]}


@mock_aws
def test_dlq_message_integration(monkeypatch):
    sqs = boto3.client("sqs", region_name="us-east-1")
    queue_url = sqs.create_queue(QueueName="dlq")["QueueUrl"]

    monkeypatch.setenv("DLQ_QUEUE_URL", "/dlq")
    monkeypatch.setenv("RETRY_QUEUE_URL", "/retry")
    monkeypatch.setenv("SQS_URL_ENDPOINT", queue_url.replace("/dlq", ""))

    handler.sqs = boto3.client("sqs", region_name="us-east-1")

    registro = {"id": 77}
    handler.enviar_registro_a_reintento_o_dlq(registro, es_dlq=True)

    msgs = sqs.receive_message(QueueUrl=queue_url)["Messages"]
    assert len(msgs) == 1

    body = json.loads(msgs[0]["Body"])
    assert body == {"OperacionesOpenFga": [registro]}

# tests/test_openfga_sync_retry_handler.py

import json
import os
import pytest
from unittest.mock import patch, Mock

import services.openfga_sync_retry_hander as handler


# ============================================================
# FIXTURE PARA VARIABLES DE ENTORNO
# ============================================================

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("RETRO_QUEUE_URL", "/retry")
    monkeypatch.setenv("DLQ_QUEUE_URL", "/dlq")
    monkeypatch.setenv("RETRY_QUEUE_URL", "/retry")  # retrocompatibilidad
    monkeypatch.setenv("SQS_URL_ENDPOINT", "https://sqs.mock.aws")


# ============================================================
# TEST 1: ENVÍO A COLA DE RETRY
# ============================================================

@patch("services.openfga_sync_retry_hander.sqs")
def test_send_retry(mock_sqs):
    registro = {"id": 1, "op": "write"}

    handler.enviar_registro_a_reintento_o_dlq(registro, es_dlq=False)

    mock_sqs.send_message.assert_called_once()

    args, kwargs = mock_sqs.send_message.call_args

    assert kwargs["QueueUrl"] == "https://sqs.mock.aws/retry"

    mensaje = json.loads(kwargs["MessageBody"])
    assert mensaje == {
        "OperacionesOpenFga": [registro]
    }


# ============================================================
# TEST 2: ENVÍO A DLQ
# ============================================================

@patch("services.openfga_sync_retry_hander.sqs")
def test_send_dlq(mock_sqs):
    registro = {"id": 2, "op": "delete"}

    handler.enviar_registro_a_reintento_o_dlq(registro, es_dlq=True)

    mock_sqs.send_message.assert_called_once()

    args, kwargs = mock_sqs.send_message.call_args

    assert kwargs["QueueUrl"] == "https://sqs.mock.aws/dlq"

    mensaje = json.loads(kwargs["MessageBody"])
    assert mensaje == {
        "OperacionesOpenFga": [registro]
    }


# ============================================================
# TEST 3: VALIDAR SERIALIZACIÓN JSON CORRECTA
# ============================================================

@patch("services.openfga_sync_retry_hander.sqs")
def test_serializacion_correcta(mock_sqs):
    registro = {"id": 99, "contenido": {"a": 1, "b": 2}}

    handler.enviar_registro_a_reintento_o_dlq(registro)

    llamado = mock_sqs.send_message.call_args[1]["MessageBody"]
    parsed = json.loads(llamado)

    assert parsed["OperacionesOpenFga"][0]["contenido"]["a"] == 1
    assert parsed["OperacionesOpenFga"][0]["contenido"]["b"] == 2


# ============================================================
# TEST 4: MANEJO DE ERRORES EN SEND_MESSAGE
# ============================================================

@patch("services.openfga_sync_retry_hander.sqs")
def test_error_en_envio(mock_sqs, caplog):
    mock_sqs.send_message.side_effect = Exception("SQS DOWN")

    registro = {"id": 123}

    handler.enviar_registro_a_reintento_o_dlq(registro, es_dlq=False)

    assert "Error enviado mensaje a sqs" in caplog.text
    assert "SQS DOWN" in caplog.text

``` 
