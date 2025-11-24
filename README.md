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
import os
import json
import logging
import boto3
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ============================================================================
# CONFIGURACIÓN BOTO3 – AHORA LAZY
# ============================================================================

_boto_config = Config(
    connect_timeout=1,
    read_timeout=2,
    retries={
        "max_attempts": 2,
        "mode": "standard"
    }
)

_sqs_client = None  # ← ya NO se crea boto3 a nivel global


def get_sqs_client():
    """
    Carga lazy: solo crea el cliente la PRIMERA VEZ que se necesite.
    Esto permite que Pytest lo parchee ANTES y que Moto lo intercepte.
    """
    global _sqs_client
    if _sqs_client is None:
        logger.debug("Inicializando cliente SQS (lazy load)")
        _sqs_client = boto3.client("sqs", config=_boto_config)
    return _sqs_client


# ============================================================================
# FUNCION PRINCIPAL: enviar_registro_a_reintento_o_dlq
# ============================================================================

def enviar_registro_a_reintento_o_dlq(registro, es_dlq=False):
    """
    Envía un registro a la cola de retry o DLQ.
    Maneja errores internos y loguea sin romper el flujo.
    """

    try:
        # Obtener endpoint base y colas desde ENV
        endpoint = os.getenv("SQS_URL_ENDPOINT", "")
        retry_suffix = os.getenv("RETRY_QUEUE_URL", "/retry")
        dlq_suffix = os.getenv("DLQ_QUEUE_URL", "/dlq")

        cola_suffix = dlq_suffix if es_dlq else retry_suffix
        queue_url = f"{endpoint}{cola_suffix}"

        body = {
            "OperacionesOpenFga": [registro]
        }

        get_sqs_client().send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(body)
        )

        logger.info(
            f"Registro enviado a {'DLQ' if es_dlq else 'RETRY'}: {cola_suffix} → {json.dumps(body)}"
        )

    except Exception as e:
        logger.error("Error enviado mensaje a sqs")
        logger.error(str(e))


# ============================================================================
# UTIL OPCIONAL PARA DEBUG
# ============================================================================

def ping():
    """Función trivial para probar importaciones sin activar boto3"""
    return "pong"

```
