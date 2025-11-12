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
