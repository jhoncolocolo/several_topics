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
```java
package examples.configuracion;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.core.io.Resource;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.security.KeyStore;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class WebClientConfigTest {

    private Resource keystoreMock;
    private WebClientConfig config;

    @BeforeEach
    void setup() throws Exception {

        // Mock del recurso keystore
        keystoreMock = mock(Resource.class);

        // Creamos un KeyStore vacío pero válido
        KeyStore ks = KeyStore.getInstance("JKS");
        ks.load(null, "123456".toCharArray());

        // Guardamos el KeyStore a bytes
        var baos = new java.io.ByteArrayOutputStream();
        ks.store(baos, "123456".toCharArray());
        byte[] keystoreBytes = baos.toByteArray();

        // Simulamos que el Resource devuelve ese InputStream
        InputStream is = new ByteArrayInputStream(keystoreBytes);
        when(keystoreMock.getInputStream()).thenReturn(is);

        // Instanciamos la config REAL con constructor
        config = new WebClientConfig(keystoreMock, "123456");
    }

    @Test
    void testWebClientCreation() throws Exception {

        WebClient client = config.webClient();

        assertNotNull(client, "El WebClient no debe ser null");

        // validamos que la baseUrl quedó configurada
        WebClient.Builder builder = WebClient.builder().baseUrl("https://midomain.com");
        assertEquals("https://midomain.com",
                client.mutate().build().toString().contains("midomain.com") ? "https://midomain.com" : null
        );

        // Verificamos que el keystore fue leído
        verify(keystoreMock, times(1)).getInputStream();
    }

    @Test
    void testWebClientThrowsExceptionOnInvalidKeystore() throws Exception {

        // Forzamos que el InputStream lance error
        Resource badResource = mock(Resource.class);
        when(badResource.getInputStream()).thenThrow(new RuntimeException("IO error"));

        WebClientConfig badConfig = new WebClientConfig(badResource, "123456");

        Exception ex = assertThrows(Exception.class, badConfig::webClient);

        assertTrue(ex.getMessage().contains("IO"), "Debe fallar por error de lectura");
    }
}


```
