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

```python
import pytest
from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler
from services.excepciones import (
    BadRequestError,
    RedisError,
    OpenFGAError,
    TransientError
)


# ========================================================================
#  TESTS BÁSICOS DEL lambda_handler
# ========================================================================

@patch("lambda_function.process_message")
def test_lambda_handler_calls_process_message(mock_pm):
    mock_pm.return_value = {"ok": True}
    event = {"x": 1}

    resp = lambda_handler(event, None)

    mock_pm.assert_called_once_with(event)
    assert resp == {"ok": True}


# ========================================================================
# UTILIDAD PARA CONSTRUIR EVENTOS DE MSK
# ========================================================================

def build_msk_event(messages):
    """
    messages = ["payload1", "payload2", ...]
    Cada mensaje debe ser dict → será serializado a JSON y luego base64.
    """
    import json, base64
    lst = []
    for msg in messages:
        encoded = base64.b64encode(json.dumps(msg).encode()).decode()
        lst.append({"value": encoded})

    return {
        "fuenteEvento": "aws:kafka",
        "records": {"partition-0": lst}
    }


# ========================================================================
# UTILIDAD PARA CONSTRUIR EVENTOS DE SQS
# ========================================================================

def build_sqs_event(messages):
    """
    messages = list of dicts
    """
    records = []
    for idx, msg in enumerate(messages):
        body = {"openfgaOperations": [msg]}
        records.append({
            "messageId": f"msg-{idx}",
            "body": json.dumps(body),
            "attributes": {"ApproximateReceiveCount": "1"},
            "fuenteEvento": "aws:sqs"
        })

    return {"Records": records}


# ========================================================================
# UTILIDAD PARA MOCKEAR process() de procesador.py
# ========================================================================

def setup_process_mock(mock_process, behaviors):
    """
    behaviors = ["ok", "bad", "retry", "skip"]
    Representa cada evento:
      ok   → process() devuelve True
      bad  → BadRequestError
      retry → Transient/Redis/OpenFGA error
      skip → process() devuelve None (idempotencia)
    """
    side_effects = []
    for b in behaviors:
        if b == "ok":
            side_effects.append(True)
        elif b == "bad":
            side_effects.append(BadRequestError("bad"))
        elif b == "retry":
            side_effects.append(TransientError("retry"))
        elif b == "skip":
            side_effects.append(None)
    mock_process.side_effect = side_effects


# ========================================================================
#  ESCENARIO A (MSK) → 1 ok, 2 fallido, 3 ok
# ========================================================================
import json

@patch("services.procesador.process")
@patch("services.procesador.enviar_registro_a_reintento_o_dlq")
def test_msk_batch_A(mock_retry, mock_process):
    setup_process_mock(mock_process, ["ok", "bad", "ok"])

    from services.procesador import proceso_kafka_evento

    ev = build_msk_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_kafka_evento(ev)

    assert resp["itemsProcesados"] == 2
    assert resp["itemsFallidos"] == 1
    assert len(resp["itemExitososBatch"]) == 2
    assert len(resp["itemFallidosBatch"]) == 1


# ========================================================================
#  ESCENARIO A (SQS)
# ========================================================================

@patch("services.procesador.process")
@patch("services.procesador.enviar_registro_a_reintento_o_dlq")
def test_sqs_batch_A(mock_retry, mock_process):
    setup_process_mock(mock_process, ["ok", "bad", "ok"])

    from services.procesador import proceso_sqs_evento

    ev = build_sqs_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_sqs_evento(ev)

    assert resp["itemsProcesados"] == 2
    assert resp["itemsFallidos"] == 1


# ========================================================================
#  ESCENARIO B (MSK) → 1 ok, 2 fallido, 3 idempotente
# ========================================================================

@patch("services.procesador.process")
@patch("services.procesador.enviar_registro_a_reintento_o_dlq")
def test_msk_batch_B(mock_retry, mock_process):
    setup_process_mock(mock_process, ["ok", "bad", "skip"])

    from services.procesador import proceso_kafka_evento

    ev = build_msk_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_kafka_evento(ev)

    assert resp["itemsProcesados"] == 1
    assert resp["itemsFallidos"] == 1


# ========================================================================
#  ESCENARIO B (SQS)
# ========================================================================

@patch("services.procesador.process")
@patch("services.procesador.enviar_registro_a_reintento_o_dlq")
def test_sqs_batch_B(mock_retry, mock_process):
    setup_process_mock(mock_process, ["ok", "bad", "skip"])

    from services.procesador import proceso_sqs_evento

    ev = build_sqs_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_sqs_evento(ev)

    assert resp["itemsProcesados"] == 1
    assert resp["itemsFallidos"] == 1


# ========================================================================
#  ESCENARIO C (MSK) → todos OK
# ========================================================================

@patch("services.procesador.process")
def test_msk_batch_C(mock_process):
    setup_process_mock(mock_process, ["ok", "ok", "ok"])

    from services.procesador import proceso_kafka_evento

    ev = build_msk_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_kafka_evento(ev)

    assert resp["itemsProcesados"] == 3
    assert resp["itemsFallidos"] == 0


# ========================================================================
#  ESCENARIO C (SQS)
# ========================================================================

@patch("services.procesador.process")
def test_sqs_batch_C(mock_process):
    setup_process_mock(mock_process, ["ok", "ok", "ok"])

    from services.procesador import proceso_sqs_evento

    ev = build_sqs_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_sqs_evento(ev)

    assert resp["itemsProcesados"] == 3
    assert resp["itemsFallidos"] == 0


# ========================================================================
#  ESCENARIO D (MSK) → todos fallan
# ========================================================================

@patch("services.procesador.process")
@patch("services.procesador.enviar_registro_a_reintento_o_dlq")
def test_msk_batch_D(mock_retry, mock_process):
    setup_process_mock(mock_process, ["bad", "retry", "retry"])

    from services.procesador import proceso_kafka_evento

    ev = build_msk_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_kafka_evento(ev)

    assert resp["itemsProcesados"] == 0
    assert resp["itemsFallidos"] == 3


# ========================================================================
#  ESCENARIO D (SQS)
# ========================================================================

@patch("services.procesador.process")
@patch("services.procesador.enviar_registro_a_reintento_o_dlq")
def test_sqs_batch_D(mock_retry, mock_process):
    setup_process_mock(mock_process, ["bad", "retry", "retry"])

    from services.procesador import proceso_sqs_evento

    ev = build_sqs_event([
        {"foo": 1},
        {"foo": 2},
        {"foo": 3}
    ])

    resp = proceso_sqs_evento(ev)

    assert resp["itemsProcesados"] == 0
    assert resp["itemsFallidos"] == 3

```
