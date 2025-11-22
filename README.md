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
    # tests/test_procesador.py

import json
import base64
import pytest
from unittest.mock import Mock

# Importamos el módulo a testear
import services.procesador as procesador_module

# Importamos las excepciones reales para simular los errores correctos
from services.excepciones import (
    BadRequestError,
    RedisError,
    TransientError,
    OpenFGAError
)

# ======================================================================
# 1. CREACIÓN DE EVENTOS MOCK PARA SIMULAR MSK Y SQS
# ======================================================================

# Evento base que usaremos en todos los tests
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

# Función helper para crear un evento MSK
def make_msk_event(payload_dict):
    # Convertimos a base64 como hacen los eventos reales de Kafka
    value = base64.b64encode(json.dumps(payload_dict).encode()).decode()
    return {
        "fuenteEvento": "aws:kafka",
        "records": {
            "miTopic-1": [{
                "value": value
            }]
        }
    }

# Función helper para crear un evento SQS
def make_sqs_event(payload_dict, attempts="1"):
    # El body es un JSON con una lista llamada openfgaOperations
    body = json.dumps({
        "openfgaOperations": [payload_dict]
    })
    return {
        "Registros": [
            {
                "fuenteEvento": "aws:sqs",
                "messageId": "id123",
                "body": body,
                "attributes": {
                    "ApproximateReceiveCount": attempts
                }
            }
        ]
    }

# ======================================================================
# 2. DummyRedis para simular distintos comportamientos de Redis
# ======================================================================

class DummyRedis:
    def __init__(self, behavior):
        # behavior es un diccionario que define qué debe retornar o lanzar save_event
        self.behavior = behavior

    def save_event(self, event, fuente, tipo):
        result = self.behavior.get("save_event")
        if isinstance(result, Exception):
            # Simula levantar una excepción real de Redis
            raise result
        return result


# ======================================================================
# 3. FIXTURE GLOBAL – aplica a TODOS los tests
# ======================================================================

@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    """
    Este fixture:
    - Reemplaza ServicioRedis por DummyRedis
    - Reemplaza funciones externas: obtener_evento_identificador y procesar_evento
    - Mockea enviar_registro_a_reintento_o_dlq para capturar llamadas
    """

    # Redis por defecto que retorna 1 (evento nuevo)
    def redis_accept():
        return DummyRedis({"save_event": 1})

    # Parcheamos ServicioRedis => devolvemos nuestro mock
    monkeypatch.setattr(procesador_module, "ServicioRedis", lambda: redis_accept())

    # Parcheamos obtener_evento_identificador => devuelve un identificador fijo
    monkeypatch.setattr(
        procesador_module,
        "obtener_evento_identificador",
        lambda ev: {"fuente": "TABLA1", "tipo": "AC"}
    )

    # Mockeamos procesar_evento
    mocked_procesar_evento = Mock()
    monkeypatch.setattr(procesador_module, "procesar_evento", mocked_procesar_evento)

    # Mockeamos enviar_registro_a_reintento_o_dlq
    mocked_retry_dlq = Mock()
    monkeypatch.setattr(procesador_module, "enviar_registro_a_reintento_o_dlq", mocked_retry_dlq)

    return {
        "mocked_procesar_evento": mocked_procesar_evento,
        "mocked_enviar_retry_dlq": mocked_retry_dlq,
        "monkeypatch": monkeypatch
    }


# ======================================================================
# 4. TESTS – cada test con explicación
# ======================================================================

def test_msk_success(patch_env):
    """
    TEST: Evento MSK exitoso.
    Validamos:
    - procesar_evento se llama 1 vez
    - no se llama retry/dlq
    """
    event = make_msk_event(BASE_EVENT)

    procesador_module.process_message(event)

    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()


def test_sqs_success_first_time(patch_env):
    """
    TEST: Evento SQS primer intento, sin errores.
    """
    event = make_sqs_event(BASE_EVENT, attempts="1")

    procesador_module.process_message(event)

    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()


def test_sqs_success_second_time(patch_env):
    """
    TEST: Evento SQS segundo intento, sin errores.
    """
    event = make_sqs_event(BASE_EVENT, attempts="2")

    procesador_module.process_message(event)

    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()


def test_openfga_badrequest_goes_to_dlq(patch_env):
    """
    TEST: BadRequestError => debe enviarse a DLQ.
    Validamos:
    - Se llamó 1 vez a enviar_registro_a_reintento_o_dlq
    - Con es_dlq=True en kwargs
    """
    patch_env["mocked_procesar_evento"].side_effect = BadRequestError("bad req")

    event = make_sqs_event(BASE_EVENT)
    procesador_module.process_message(event)

    # Verificar la llamada
    patch_env["mocked_enviar_retry_dlq"].assert_called_once()

    # Extraemos args y kwargs de la llamada del mock
    _, kwargs = patch_env["mocked_enviar_retry_dlq"].call_args

    # Verificamos el flag correcto
    assert kwargs.get("es_dlq") is True


def test_redis_error_sends_retry(patch_env):
    """
    TEST: RedisError => debe enviarse a cola de retry (no DLQ).
    """

    # Este DummyRedis simula que save_event levanta RedisError
    def redis_raise():
        return DummyRedis({"save_event": RedisError("redis down")})

    patch_env["monkeypatch"].setattr(procesador_module, "ServicioRedis", lambda: redis_raise())

    event = make_sqs_event(BASE_EVENT)
    procesador_module.process_message(event)

    patch_env["mocked_enviar_retry_dlq"].assert_called_once()

    _, kwargs = patch_env["mocked_enviar_retry_dlq"].call_args
    assert kwargs.get("es_dlq") is False


def test_unexpected_exception_goes_retry(patch_env):
    """
    TEST: Excepción inesperada => debe enviarse a retry.
    """

    patch_env["mocked_procesar_evento"].side_effect = Exception("boom")

    event = make_sqs_event(BASE_EVENT)
    procesador_module.process_message(event)

    patch_env["mocked_enviar_retry_dlq"].assert_called_once()

    _, kwargs = patch_env["mocked_enviar_retry_dlq"].call_args
    assert kwargs.get("es_dlq") is False

def test_redis_save_event_return_zero_ignores(patch_env):
    def redis_zero():
        return DummyRedis({"save_event": 0})

    patch_env["monkeypatch"].setattr(procesador_module, "ServicioRedis", lambda: redis_zero())

    event = make_sqs_event(BASE_EVENT)

    procesador_module.process_message(event)

    patch_env["mocked_procesar_evento"].assert_not_called()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()

def test_redis_more_recent_event_ignores_sqs_retry(patch_env):
    def redis_zero():
        return DummyRedis({"save_event": 0})

    patch_env["monkeypatch"].setattr(procesador_module, "ServicioRedis", lambda: redis_zero())

    event = make_sqs_event(BASE_EVENT, attempts="3")

    procesador_module.process_message(event)

    patch_env["mocked_procesar_evento"].assert_not_called()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()

    ```
