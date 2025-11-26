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
package examples.configuracion;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.core.io.Resource;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.web.reactive.function.client.WebClient;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.security.KeyStore;

import javax.net.ssl.KeyManagerFactory;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class WebClientConfigTest {

    private WebClientConfig config;

    private Resource keystoreMock;

    private InputStream inputStreamMock;

    @BeforeEach
    void setUp() throws Exception {
        config = new WebClientConfig();

        // Mock del Resource
        keystoreMock = mock(Resource.class);

        // Mock del InputStream (contenido simulado del keystore)
        inputStreamMock = new ByteArrayInputStream(new byte[]{1, 2, 3});

        // Inyectar valores simulados a las @Value
        ReflectionTestUtils.setField(config, "keystore", keystoreMock);
        ReflectionTestUtils.setField(config, "keystorePassword", "123456");

        // Simular que load() no falle
        when(keystoreMock.getInputStream()).thenReturn(inputStreamMock);

        // Mock parcial del KeyStore estático
        KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
        ReflectionTestUtils.invokeMethod(ks, "load", (InputStream) null, "123456".toCharArray());

        // 🔥 MOCK estático: evitar que Spring cargue un keystore real
        Mockito.mockStatic(KeyStore.class).when(() -> KeyStore.getInstance("MYINSTANCE")).thenReturn(ks);

        // MOCK de KeyManagerFactory
        KeyManagerFactory kmf = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        kmf.init(ks, "123456".toCharArray());
        Mockito.mockStatic(KeyManagerFactory.class)
                .when(() -> KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm()))
                .thenReturn(kmf);
    }

    @Test
    void testWebClientBeanCreation() throws Exception {
        WebClient webClient = config.webClient();

        assertThat(webClient).isNotNull();
        assertThat(webClient).isInstanceOf(WebClient.class);

        // Verificar que se llamó getInputStream()
        verify(keystoreMock, times(1)).getInputStream();
    }

    @Test
    void testWebClientHasBaseUrl() throws Exception {
        WebClient webClient = config.webClient();

        String baseUrl = (String) ReflectionTestUtils.getField(webClient, "baseUrl");
        assertThat(baseUrl).isEqualTo("https://midomain.com");
    }
}

```
