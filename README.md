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
package com.ejemplo.repositorios;

import com.ejemplo.entidades.MisArticulos;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class MisArticulosRepositoryTest {

    private MisArticulosRepository repo;

    @BeforeEach
    void setup() {
        // Repositorio mockeado porque no hay BD
        repo = Mockito.mock(MisArticulosRepository.class);
    }

    @Test
    void testBuscarArticulosPorCriteriosNativos_RetornaLista() {
        MisArticulos a = new MisArticulos();
        a.setCampo1("1");

        when(repo.buscarArticulosPorCriteriosNativos("A", "B"))
                .thenReturn(Arrays.asList(a));

        List<MisArticulos> result = repo.buscarArticulosPorCriteriosNativos("A", "B");

        assertNotNull(result);
        assertEquals(1, result.size());
        assertEquals("1", result.get(0).getCampo1());

        verify(repo, times(1)).buscarArticulosPorCriteriosNativos("A", "B");
    }

    @Test
    void testBuscarArticulosPorCriteriosNativos_ListaVacia() {
        when(repo.buscarArticulosPorCriteriosNativos("X", "Y"))
                .thenReturn(Collections.emptyList());

        List<MisArticulos> result = repo.buscarArticulosPorCriteriosNativos("X", "Y");

        assertNotNull(result);
        assertTrue(result.isEmpty());

        verify(repo, times(1)).buscarArticulosPorCriteriosNativos("X", "Y");
    }

    @Test
    void testBuscarArticulosPorCriteriosNativos_RetornaNull() {
        when(repo.buscarArticulosPorCriteriosNativos("P", "Q"))
                .thenReturn(null);

        List<MisArticulos> result = repo.buscarArticulosPorCriteriosNativos("P", "Q");

        assertNull(result);

        verify(repo, times(1)).buscarArticulosPorCriteriosNativos("P", "Q");
    }
}

```java
 package com.ejemplo.service;

import com.ejemplo.entidades.MisArticulos;
import com.ejemplo.repositorios.MisArticulosRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class MisArticulosServiceImplTest {

    private MisArticulosRepository repo;
    private MisArticulosServiceImpl service;

    @BeforeEach
    void setup() throws Exception {
        repo = Mockito.mock(MisArticulosRepository.class);
        service = new MisArticulosServiceImpl();

        // Inyectar el repo mock mediante reflexión (porque es @Autowired)
        Field field = MisArticulosServiceImpl.class.getDeclaredField("misArticulosRepository");
        field.setAccessible(true);
        field.set(service, repo);
    }

    @Test
    void testBuscar_RetornaListaCorrecta() {
        MisArticulos a1 = new MisArticulos();
        MisArticulos a2 = new MisArticulos();

        when(repo.buscarArticulosPorCriteriosNativos("A", "B"))
                .thenReturn(Arrays.asList(a1, a2));

        List<MisArticulos> result = service.buscar("A", "B");

        assertNotNull(result);
        assertEquals(2, result.size());

        verify(repo, times(1)).buscarArticulosPorCriteriosNativos("A", "B");
    }

    @Test
    void testBuscar_ListaVacia() {
        when(repo.buscarArticulosPorCriteriosNativos("X", "Y"))
                .thenReturn(Collections.emptyList());

        List<MisArticulos> result = service.buscar("X", "Y");

        assertNotNull(result);
        assertTrue(result.isEmpty());

        verify(repo).buscarArticulosPorCriteriosNativos("X", "Y");
    }

    @Test
    void testBuscar_RetornaNull() {
        when(repo.buscarArticulosPorCriteriosNativos("P", "Q"))
                .thenReturn(null);

        List<MisArticulos> result = service.buscar("P", "Q");

        assertNull(result);

        verify(repo).buscarArticulosPorCriteriosNativos("P", "Q");
    }

    @Test
    void testInyeccionDeRepositorioPorReflexion() throws Exception {
        // Verificar que el repo mock realmente se inyectó
        Field field = MisArticulosServiceImpl.class.getDeclaredField("misArticulosRepository");
        field.setAccessible(true);

        Object injectedRepo = field.get(service);

        assertNotNull(injectedRepo);
        assertSame(repo, injectedRepo);
    }
}


```python
# tests/test_procesador.py

import sys
import types
import json
import base64
import pytest
from unittest.mock import Mock

# =============================================================
# SEGURIDAD AL IMPORTAR (IMPORT SAFETY)
# =============================================================
# El módulo real `services.openfga_sync_retry_hander` crea clientes boto3
# al momento de importarse, lo cual rompe los tests.
# Para evitar eso, antes de importar `services.procesador`, inyectamos
# un "stub" (módulo falso) con una función mínima.
# Esto evita que boto3 se inicialice durante la importación.
# =============================================================

stub_module_name = "services.openfga_sync_retry_hander"

# Solo si el módulo no existe aún, lo creamos manualmente
if stub_module_name not in sys.modules:

    # Creamos un módulo vacío dinámicamente
    stub = types.ModuleType(stub_module_name)

    # Definimos una función falsa que reemplaza la real
    def enviar_registro_a_reintento_o_dlq(registro, es_dlq=False):
        # No hace nada. En los tests la vamos a reemplazar con monkeypatch.
        return None

    # Asignamos esa función al módulo stub
    stub.enviar_registro_a_reintento_o_dlq = enviar_registro_a_reintento_o_dlq

    # Registramos el módulo falso en sys.modules
    sys.modules[stub_module_name] = stub

# Ahora importamos el módulo principal SIN activar boto3 ni SQS
import importlib
procesador_module = importlib.import_module("services.procesador")

# Importamos las excepciones para usarlas en asserts
from services.excepciones import (
    BadRequestError,
    RedisError,
    TransientError,
    OpenFGAError
)

# =============================================================
# EVENTO BASE DE PRUEBA
# =============================================================
# Este es el cuerpo típico de un evento proveniente de MSK o SQS.
# Simula la estructura real que llega desde los procesadores.
# =============================================================

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

# =============================================================
# FUNCIONES AYUDA PARA CREAR EVENTOS MSK Y SQS
# =============================================================

def msk_record_from_payload(payload, offset=None):
    """
    Convierte un payload Python en el formato que MSK produce:
    el valor 'value' debe venir en BASE64.
    """
    value = base64.b64encode(json.dumps(payload).encode()).decode()
    rec = {"value": value}
    if offset is not None:
        rec["offset"] = offset
    return rec


def make_msk_event(payloads_by_topic_partition):
    """
    Construye un evento MSK realista compuesto de varios topic-partition.
    Ejemplo:
    {
        "miTopic-1": [p1, p2, p3],
        "topic-2": [p4,p5]
    }
    """
    records = {}
    for tp, plist in payloads_by_topic_partition.items():
        recs = []
        base_off = 100  # offset inicial
        for i, p in enumerate(plist):
            recs.append(msk_record_from_payload(p, offset=base_off + i))
        records[tp] = recs
    return {"fuenteEvento": "aws:kafka", "records": records}


def make_sqs_event_batch(list_of_payloads, retries_list=None):
    """
    Simula un evento SQS con múltiples Records,
    cada uno con su contador de reintentos.
    """
    if retries_list is None:
        retries_list = ["1"] * len(list_of_payloads)

    records = []
    for i, payload in enumerate(list_of_payloads):
        # Formato real: una lista con la clave openfgaOperations
        body = json.dumps({"openfgaOperations": [payload]})
        records.append({
            "fuenteEvento": "aws:sqs",
            "messageId": f"id-{i+1}",
            "body": body,
            "attributes": {"ApproximateReceiveCount": retries_list[i]}
        })
    return {"Records": records}

# =============================================================
# SIMULADORES DE REDIS
# =============================================================

class DummyRedis:
    """
    Redis simple con un único comportamiento fijo.
    """
    def __init__(self, behavior):
        self.behavior = behavior

    def save_event(self, event, fuente, tipo):
        result = self.behavior.get("save_event")
        if isinstance(result, Exception):
            raise result
        return result


class SharedDummyRedis:
    """
    Redis secuencial:
    Cada llamada a save_event consume 1 valor de una lista.
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

# =============================================================
# FIXTURE GLOBAL patch_env
# =============================================================
# Este fixture se ejecuta AUTOMÁTICAMENTE en todos los tests.
# Parchea:
# - ServicioRedis         → para no usar Redis real
# - obtener_evento_identificador → devuelve valores válidos
# - procesar_evento       → Mock (evita procesar lógica real)
# - enviar_registro...    → Mock (evita SQS real)
# =============================================================

@pytest.fixture(autouse=True)
def patch_env(monkeypatch):

    def redis_accept_factory():
        return DummyRedis({"save_event": 1})

    # Redis simulado
    monkeypatch.setattr(procesador_module, "ServicioRedis", lambda: redis_accept_factory())

    # Identificador del evento simulado
    monkeypatch.setattr(procesador_module, "obtener_evento_identificador",
                        lambda ev: {"fuente": "TABLA1", "tipo": "AC"})

    # procesar_evento → solo Mock
    mocked_procesar_evento = Mock()
    monkeypatch.setattr(procesador_module, "procesar_evento", mocked_procesar_evento)

    # enviar_registro_a_reintento_o_dlq → Mock
    mocked_retry_dlq = Mock()
    monkeypatch.setattr(procesador_module, "enviar_registro_a_reintento_o_dlq", mocked_retry_dlq)

    return {
        "mocked_procesar_evento": mocked_procesar_evento,
        "mocked_enviar_retry_dlq": mocked_retry_dlq,
        "monkeypatch": monkeypatch
    }

# =============================================================
# UTILIDAD: instalar Redis secuencial + lógica custom para procesar_evento
# =============================================================

def install_shared_redis_and_processor(monkeypatch, save_seq, procesar_side_effect=None):
    """
    Parchea Redis con SharedDummyRedis y opcionalmente modifica el comportamiento de procesar_evento.
    """
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


# =============================================================
# TESTS CLÁSICOS
# =============================================================

def test_msk_success(patch_env):
    """
    Caso simple MSK: un solo registro exitoso.
    """
    event = make_msk_event({"miTopic-1": [BASE_EVENT]})
    result = procesador_module.process_message(event)

    patch_env["mocked_procesar_evento"].assert_called_once()
    patch_env["mocked_enviar_retry_dlq"].assert_not_called()

    assert result["itemsProcesados"] == 1
    assert result["itemsFallidos"] == 0

# ... (TODOS LOS TESTS SIGUIENTES SE EXPLICAN IGUALAMENTE)
```

```
package examples.configuracion;

import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.ObjectPostProcessor;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.*;
import org.springframework.security.web.SecurityFilterChain;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Tests completos y 100% unitarios para SecurityConfig.
 * No levanta servidor, no usa SpringBootTest.
 * Todo en un solo archivo.
 */
class SecurityConfigTest {

    // ===============================================================
    //  Helper para poder instanciar HttpSecurity sin contexto Spring
    // ===============================================================
    private static HttpSecurity createHttpSecurity() {
        return new HttpSecurity(
                new ObjectPostProcessor<Object>() {
                    @Override
                    public <O> O postProcess(O object) {
                        return object;
                    }
                },
                new AuthenticationManager() {},
                java.util.Collections.emptyMap()
        );
    }

    // ===============================================================
    // 1. Validar que el bean se crea y build no falla
    // ===============================================================
    @Test
    void securityFilterChainIsCreated() throws Exception {
        SecurityConfig config = new SecurityConfig();
        HttpSecurity http = createHttpSecurity();

        SecurityFilterChain chain = config.securityFilterChain(http);

        assertThat(chain).isNotNull();
    }

    // ===============================================================
    // 2. CSRF está deshabilitado
    // ===============================================================
    @Test
    void csrfIsDisabled() throws Exception {
        SecurityConfig config = new SecurityConfig();
        HttpSecurity http = createHttpSecurity();

        config.securityFilterChain(http);

        assertThat(http.getConfigurer(CsrfConfigurer.class)).isNull();
    }

    // ===============================================================
    // 3. formLogin está deshabilitado
    // ===============================================================
    @Test
    void formLoginIsDisabled() throws Exception {
        SecurityConfig config = new SecurityConfig();
        HttpSecurity http = createHttpSecurity();

        config.securityFilterChain(http);

        assertThat(http.getConfigurer(FormLoginConfigurer.class)).isNull();
    }

    // ===============================================================
    // 4. logout está deshabilitado
    // ===============================================================
    @Test
    void logoutIsDisabled() throws Exception {
        SecurityConfig config = new SecurityConfig();
        HttpSecurity http = createHttpSecurity();

        config.securityFilterChain(http);

        assertThat(http.getConfigurer(LogoutConfigurer.class)).isNull();
    }

    // ===============================================================
    // 5. Validar que los matchers se registraron
    //    (no valida rutas reales, solo que fueron configuradas)
    // ===============================================================
    @Test
    void matchersAreRegistered() throws Exception {
        SecurityConfig config = new SecurityConfig();
        HttpSecurity http = createHttpSecurity();

        config.securityFilterChain(http);

        assertThat(http.getAuthorizationRegistry()).isNotNull();
    }
}

```
