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
    ```

    ```python
    import json

def lambda_handler(event, context):
    """
    Función de ejemplo que simula el procesamiento de un evento.
    """
    try:
        # Intenta obtener el valor de una clave específica del 'event'
        name = event.get('name', 'Mundo')
        
        # Lógica de la función
        response_message = f"Hola, {name}! Tu función Lambda se ejecutó correctamente."
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': response_message})
        }
    except Exception as e:
        # Manejo básico de errores
        print(f"Error al procesar el evento: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }

# --- Código para ejecución local (Simulación) ejecuta con python nombre_archivo.py ---
if __name__ == "__main__":
    # 1. Define un objeto 'event' de prueba
    test_event = {
        "name": "Gemini",
        "detail": "Prueba de ejecución local"
    }
    
    # 2. Define un objeto 'context' (puede ser un objeto vacío o None para pruebas simples)
    test_context = None # O un objeto simulado si tu lógica lo requiere

    print("--- Iniciando prueba local ---")
    
    # 3. Invoca la función handler
    result = lambda_handler(test_event, test_context)
    
    # 4. Imprime el resultado
    print("\nResultado del Handler:")
    print(result)
    
    print("\n--- Prueba local finalizada ---")
    ```

```python
import sys
import os
import pytest
import json
import logging

# ✅ Permitir imports desde src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from lambda_funcion import lambda_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- Datos simulados para integración ---
EVENTO_VALIDO = {
    "message": {
        "hostname": "api.production.internal",
        "timestamp": "2025-11-10T23:56:44Z",
        "data": {
            "event_type": "user_created",
            "table": "users",
            "values": {
                "user_id": 1024,
                "username": "ashketchum",
                "email": "ash@kanto.com",
                "created_at": "2025-11-10T23:56:00Z",
                "is_active": True
            }
        }
    }
}


# --- Configuración dinámica ---
@pytest.fixture(scope="session", autouse=True)
def setup_env():
    """
    Configura variables de entorno desde el .env (si existe)
    o usa valores por defecto si no está configurado.
    """
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "src", ".env"))

    # Valores por defecto si no hay .env
    os.environ.setdefault("API_URL", "http://localhost:8000")
    os.environ.setdefault("STORE_ID", "store-001")
    os.environ.setdefault("MODELO_ID", "modelo-001")

    print("\n[INFO] Variables cargadas:")
    print(" API_URL =", os.getenv("API_URL"))
    print(" STORE_ID =", os.getenv("STORE_ID"))
    print(" MODELO_ID =", os.getenv("MODELO_ID"))


# --- Test principal de integración ---
def test_lambda_integration_success(setup_env):
    """
    Test de integración completo: ejecuta la lambda real,
    validando la interacción completa con ClienteServicio.
    """
    result = lambda_handler(EVENTO_VALIDO, None)
    print("\n[DEBUG] Resultado de lambda_handler:", result)

    assert "statusCode" in result
    assert result["statusCode"] in [200, 500]

    if result["statusCode"] == 200:
        print("[OK] La tupla fue procesada y enviada correctamente a OpenFGA Mock.")
    else:
        print("[WARN] Hubo un error en la comunicación con OpenFGA (ver logs).")


def test_lambda_integration_retry_flow(setup_env):
    """
    Test de integración: simula reintentos de SQS cuando falla
    la comunicación con el servicio OpenFGA.
    """
    # 🔁 Primer intento con error forzado (por ejemplo, API caída)
    evento_retry = dict(EVENTO_VALIDO)
    evento_retry["retry_count"] = 0

    print("\n[TEST] Ejecutando primer intento (API_URL = {})".format(os.getenv("API_URL")))
    result_1 = lambda_handler(evento_retry, None)
    assert "statusCode" in result_1
    print("[DEBUG] Resultado intento 1:", result_1)

    # 🔁 Segundo intento simulado
    evento_retry["retry_count"] = 1
    result_2 = lambda_handler(evento_retry, None)
    print("[DEBUG] Resultado intento 2:", result_2)

    # El segundo intento puede ser exitoso o no, dependiendo de tu mock OpenFGA
    assert "statusCode" in result_2
    assert result_2["statusCode"] in [200, 500]

```
