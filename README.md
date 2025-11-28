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
```txt




# =========================================================
# Archivo: src\lambda_function.py
# =========================================================
# src\lambda_function.py

import logging
import json
import os
import services.procesador as procesador
import services.openfga_sync_retry_hander as retry_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DLQ_URL = os.getenv("DLQ_QUEUE_URL", "MOCK_DLQ")
RETRY_URL = os.getenv("RETRY_QUEUE_URL", "MOCK_RETRY")

def safe_json(data):
    def fix(o):
        if isinstance(o, bytes):
            try:
                return o.decode("utf-8")
            except:
                return str(o)
        return o

    return json.dumps(data, default=fix)

def lambda_handler(event, context):
    logger.info(f"Lambda invoked. Event: {safe_json(event)}")


    batch_log = procesador.process_message(event)

    # ---------------------------------------------------------
    # 1) MANEJO PARA EVENTOS MSK  (NO HAY PARTIAL BATCH)
    # ---------------------------------------------------------
    if batch_log["origen"] == "MSK":

        for item in batch_log["itemFallidosBatch"]:
            destino = item["destino"]

            if destino == "RETRY":
                retry_handler.enviar_registro_a_reintento_o_dlq(
                    evento=item["evento"],
                    queue_url=RETRY_URL,
                    destino="RETRY"
                )

            elif destino == "DLQ":
                retry_handler.enviar_registro_a_reintento_o_dlq(
                    evento=item["evento"],
                    queue_url=DLQ_URL,
                    destino="DLQ"
                )

        return {"status": "ok", "processed": batch_log["itemsProcesados"]}

    # ---------------------------------------------------------
    # 2) MANEJO PARA SQS (PARCIAL BATCH)
    # ---------------------------------------------------------
    failures = []

    for item in batch_log["itemFallidosBatch"]:
        msg_id = item["itemIdentificador"]
        destino = item["destino"]

        if destino == "RETRY":
            failures.append({"itemIdentifier": msg_id})

        elif destino == "DLQ":
            retry_handler.enviar_registro_a_reintento_o_dlq(
                evento=item["evento"],
                queue_url=DLQ_URL,
                destino="DLQ"
            )

    response = {"batchItemFailures": failures}
    logger.info(f"Lambda response for SQS partial batch: {safe_json(response)}")
    return response


# =========================================================
# Archivo: src\services\openfga_sync_retry_hander.py
# =========================================================
# src/services/openfga_sync_retry_hander.py
import json
import logging
import boto3
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_boto_config = Config(
    connect_timeout=1,
    read_timeout=2,
    retries={"max_attempts": 2, "mode": "standard"}
)

_sqs_client = None


def get_sqs_client():
    global _sqs_client
    if _sqs_client is None:
        logger.debug("Inicializando cliente SQS (lazy load)")
        _sqs_client = boto3.client("sqs", config=_boto_config)
    return _sqs_client


def enviar_registro_a_reintento_o_dlq(*, evento, queue_url, destino):
    """
    Publica un mensaje en DLQ o Retry.
    Se usa solo con kwargs → esto permite que pytest inspeccione correctamente call_args.kwargs.
    """
    try:
        body = {"OperacionesOpenFga": [evento]}

        logger.info(
            f"[OpenFGA Retry Handler] Publicando mensaje a {destino} → {queue_url}"
        )

        get_sqs_client().send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(body)
        )

        logger.info(
            f"[OpenFGA Retry Handler] Mensaje enviado correctamente a {destino}: {json.dumps(body)}"
        )

    except Exception as e:
        logger.error(
            f"[OpenFGA Retry Handler] Error enviando mensaje a {destino}: {e}",
            exc_info=True
        )
        raise


def ping():
    return "pong"



# =========================================================
# Archivo: src\services\procesador.py
# =========================================================
# src/services/procesador.py

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

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def safe_json(data):
    def fix(o):
        if isinstance(o, bytes):
            try:
                return o.decode("utf-8")
            except:
                return str(o)
        return o

    return json.dumps(data, default=fix)

    
# --------------------------------------------------------------------
#   CLASIFICACIÓN DE EVENTOS
# --------------------------------------------------------------------

def process_message(event):
    """
    Punto de entrada: detecta tipo MSK o SQS y delega.
    Ahora cada batch genera bitácora.
    """
    logger.info("even in process_message")
    logger.info(safe_json(event))

    if es_evento_kafka(event):
        return proceso_kafka_evento(event)

    elif es_evento_sqs(event):
        return proceso_sqs_evento(event)

    else:
        logger.error("Origen de evento no reconocido")
        raise ValueError("Origen de evento no reconocido")


def es_evento_kafka(event):
    if 'eventSource' in event:
        return event.get('eventSource') == 'aws:kafka'
    return event.get('eventSource') == 'aws:kafka'


def es_evento_sqs(event):
    if 'Records' not in event or not event['Records']:
        return False
    first = event['Records'][0]
    return first.get('eventSource') == 'aws:sqs' or first.get('eventSource') == 'aws:sqs'


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
    logger.info("MSK Batch Log: " + safe_json(batch_log))
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

    logger.info("SQS Batch Log: " + safe_json(batch_log))
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

        # Nota: aquí esperamos que el body sea {"OperacionesOpenFga": [registro]}
        registro = body["OperacionesOpenFga"][0]
        registro["messageId"] = record.get("messageId")
        registro["retry"] = record["attributes"].get("ApproximateReceiveCount", "1")
        # Guardamos receiptHandle y atributos por si se necesitan en traces
        registro["_sqs_receiptHandle"] = record.get("receiptHandle")
        registro["_sqs_attributes"] = record.get("attributes", {})

        listado_registros.append(registro)

    return listado_registros


# --------------------------------------------------------------------
#   PROCESO INDIVIDUAL CON BITÁCORA (NUEVO)
# --------------------------------------------------------------------

def process_with_log(event, batch_log):
    """
    Ejecuta process() y actualiza bitácora.
    Este es el ÚNICO lugar responsable de clasificar destino (DLQ/RETRY).
    """
    try:
        result = process(event)

        if result is None:
            # idempotencia: Redis dijo que ya fue procesado
            logger.info(f"Evento ignorado (idempotencia): {event.get('messageId')}")
            batch_log["itemExitososBatch"].append({
                "itemIdentificador": event.get("messageId"),
                "numeroReintento": event.get("retry"),
                "nota": "idempotente"
            })
            return

        # ÉXITO
        batch_log["itemsProcesados"] += 1
        batch_log["itemExitososBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry")
        })

    except BadRequestError:
        # Error NO reintentable ─→ DLQ (no lo enviamos aquí; solo lo marcamos para que el handler lo haga)
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry"),
            "error": "BadRequestError",
            "destino": "DLQ",
            "evento": event  # guardamos evento para que el handler lo envíe a DLQ
        })

    except (RedisError, OpenFGAError, TransientError) as e:
        # Error reintentable ─→ RETRY (dejar que SQS lo maneje con Partial Batch Response)
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry"),
            "error": e.__class__.__name__,
            "destino": "RETRY",
            "evento": event
        })

    except Exception as e:
        # Error inesperado ─→ RETRY (por seguridad)
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event.get("messageId"),
            "numeroReintento": event.get("retry"),
            "error": "UnexpectedError",
            "destino": "RETRY",
            "message": str(e),
            "evento": event
        })


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
    # Si no tienes Redis en integración, deberías simularlo en tests.
    redis = ServicioRedis()
    event_identifier = obtener_evento_identificador(event)
    logger.info("event_identifier: %s", event_identifier)
    new_event = redis.guardar_evento(event, event_identifier["fuente"], event_identifier["tipo"])

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







# =========================================================
# Archivo: tests\mocks_aws.txt
# =========================================================
# services/servicio_redis.py

class ServicioRedis:
    def guardar_evento(self, event, fuente, tipo):
        # simula idempotencia básica
        return True


# services/procesador.py
def process(event):
    if event.get("val") == "OK":
        return True
    if event.get("val") == "RETRY":
        raise TransientError("Falla temporal")
    if event.get("val") == "DLQ":
        raise BadRequestError("Error malo")
    return True


# =========================================================
# Archivo: tests\test_lambda_partial_response.py
# =========================================================
# tests/test_lambda_partial_response.py
import json
from unittest.mock import patch
from src.lambda_function import lambda_handler


def make_event_with_records(message_ids):
    return {
        "Records": [
            {
                "messageId": mid,
                "body": json.dumps({
                    "OperacionesOpenFga": [
                        {"foo": "bar"}
                    ]
                }),
                "attributes": {"ApproximateReceiveCount": "1"},
                "EventSource": "aws:sqs"
            }
            for mid in message_ids
        ]
    }


@patch("services.procesador.process_message")
@patch("services.openfga_sync_retry_hander.enviar_registro_a_reintento_o_dlq")
def test_lambda_handler_marks_retry_and_sends_dlq(mock_send_dlq, mock_process_message):
    """
    Escenario:
    - msg-1 -> RETRY
    - msg-2 -> DLQ
    - msg-3 -> OK
    """
    batch_log = {
        "origen": "SQS",
        "itemsProcesados": 1,
        "itemsFallidos": 2,
        "itemExitososBatch": [
            {"itemIdentificador": "msg-3", "numeroReintento": "1"}
        ],
        "itemFallidosBatch": [
            {"itemIdentificador": "msg-1", "numeroReintento": "1",
             "error": "TransientError", "destino": "RETRY", "evento": {"messageId": "msg-1"}},

            {"itemIdentificador": "msg-2", "numeroReintento": "1",
             "error": "BadRequestError", "destino": "DLQ", "evento": {"messageId": "msg-2"}}
        ]
    }

    mock_process_message.return_value = batch_log

    ev = make_event_with_records(["msg-1", "msg-2", "msg-3"])

    resp = lambda_handler(ev, None)

    assert "batchItemFailures" in resp
    failures = resp["batchItemFailures"]

    assert {"itemIdentifier": "msg-1"} in failures
    assert {"itemIdentifier": "msg-2"} not in failures
    assert {"itemIdentifier": "msg-3"} not in failures

    # ============================
    # Validar llamada al DLQ
    # ============================
    assert mock_send_dlq.call_count == 1

    kwargs = mock_send_dlq.call_args.kwargs

    assert kwargs["destino"] == "DLQ"
    assert kwargs["queue_url"] == "MOCK_DLQ"
    assert kwargs["evento"] == {"messageId": "msg-2"}



# =========================================================
# Archivo: tests\test_procesador.py
# =========================================================
import pytest
import json
from unittest.mock import patch
import services.procesador as procesador


# ============================================================
# Mock correcto para Secrets Manager
# ============================================================

@pytest.fixture(autouse=True)
def mock_secret_manager():
    with patch(
        "utilitarios.acceso_gestor_secretos.obtener_datos_secretos",
        return_value={
            "openfga": json.dumps({
                "API_URL": "http://fake",
                "STORE_ID": "abc",
                "MODEL_ID": "123"
            }),
            "redis": json.dumps({
                "REDIS_HOST": "localhost",
                "REDIS_PORT": 6379,
                "REDIS_USER": "u",
                "REDIS_PASS": "p",
                "REDIS_TTL": 20
            })
        }
    ):
        yield


# ============================================================
# SQS EVENT
# ============================================================

SQS_EVENT = {
    "Records": [
        {
            "eventSource": "aws:sqs",
            "messageId": "111-222",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": """{
                "OperacionesOpenFga": [
                    {"id": "123", "accion": "probar"}
                ]
            }"""
        }
    ]
}


# ============================================================
# MSK TESTS
# ============================================================

def test_msk_ok():
    evento = {"eventSource": "aws:kafka", "value": "test"}
    result = procesador.process_message(evento)
    assert result["origen"] == "MSK"


def test_msk_retry():
    evento = {"eventSource": "aws:kafka", "value": "retry"}
    result = procesador.process_message(evento)
    assert result["origen"] == "MSK"


def test_msk_dlq():
    evento = {"eventSource": "aws:kafka", "value": "dlq"}
    result = procesador.process_message(evento)
    assert result["origen"] == "MSK"


# ============================================================
# SQS TESTS
# ============================================================

@patch("services.procesador.procesar_evento")
def test_sqs_ok(mock_proc):
    mock_proc.return_value = {"status": "ok"}

    procesador.process_message(SQS_EVENT)

    mock_proc.assert_called_once()


@patch("services.procesador.procesar_evento")
def test_sqs_retry(mock_proc):
    mock_proc.return_value = {"retry": True}

    procesador.process_message(SQS_EVENT)

    mock_proc.assert_called_once()


@patch("services.procesador.procesar_evento")
def test_sqs_dlq(mock_proc):
    mock_proc.return_value = {"dlq": True}

    procesador.process_message(SQS_EVENT)

    mock_proc.assert_called_once()

```
