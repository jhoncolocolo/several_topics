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
package com.ejemplo.repositorios; // Asegúrate de ajustar el paquete

import com.ejemplo.entidades.MisArticulos;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

// Configura un entorno de prueba para JPA y una base de datos en memoria (H2 por defecto)
@DataJpaTest
// Opcional: Para asegurar que usa la base de datos de reemplazo en memoria y no la real
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
public class MisArticulosRepositoryTest {

    // Inyectamos el repositorio a probar
    @Autowired
    private MisArticulosRepository repository;

    // Constantes para los valores
    private static final String MATCH_C3 = "clave3";
    private static final String MATCH_C4 = "clave4";
    private static final String VALUE1 = "valor1";
    private static final String VALUE2 = "valor2";
    private static final String NO_MATCH = "no_coincide";

    /**
     * Inicializa la base de datos antes de cada prueba.
     * Insertamos datos para tener casos de éxito y de fallo.
     */
    @BeforeEach
    void setUp() {
        // Limpiamos por si acaso, aunque @DataJpaTest debería hacerlo
        repository.deleteAll();

        // 1. Artículo que DEBE COINCIDIR (cumple todos los criterios)
        MisArticulos articulo1 = new MisArticulos(
            1L, "a1", VALUE1, MATCH_C3, MATCH_C4, "x1"
        );

        // 2. Artículo que DEBE COINCIDIR (cumple todos los criterios con VALUE2)
        MisArticulos articulo2 = new MisArticulos(
            2L, "a2", VALUE2, MATCH_C3, MATCH_C4, "x2"
        );

        // 3. Artículo que NO COINCIDE (campo3 incorrecto)
        MisArticulos articulo3 = new MisArticulos(
            3L, "a3", VALUE1, NO_MATCH, MATCH_C4, "x3"
        );

        // 4. Artículo que NO COINCIDE (campo4 incorrecto)
        MisArticulos articulo4 = new MisArticulos(
            4L, "a4", VALUE1, MATCH_C3, NO_MATCH, "x4"
        );

        // 5. Artículo que NO COINCIDE (campo2 incorrecto, no es 'valor1' ni 'valor2')
        MisArticulos articulo5 = new MisArticulos(
            5L, "a5", NO_MATCH, MATCH_C3, MATCH_C4, "x5"
        );

        repository.saveAll(Arrays.asList(articulo1, articulo2, articulo3, articulo4, articulo5));
    }

    // --- PRUEBAS ---

    @Test
    void cuandoBuscarArticulosPorCriteriosNativos_entoncesDevuelveSoloCoincidentes() {
        // GIVEN (Dados)
        // Valores de búsqueda
        String paramCampo3 = MATCH_C3;
        String paramCampo4 = MATCH_C4;
        Collection<String> posiblesValoresCampo2 = Arrays.asList(VALUE1, VALUE2);

        // WHEN (Cuando)
        List<MisArticulos> resultados = repository.buscarArticulosPorCriteriosNativos(
            paramCampo3,
            paramCampo4,
            posiblesValoresCampo2
        );

        // THEN (Entonces)
        // 1. Debe haber exactamente 2 resultados
        assertThat(resultados).isNotNull();
        assertThat(resultados).hasSize(2);

        // 2. Verificamos que los IDs de los resultados sean los esperados (1L y 2L)
        List<Long> idsEncontrados = resultados.stream()
            .map(MisArticulos::getId)
            .toList();

        assertThat(idsEncontrados).containsExactlyInAnyOrder(1L, 2L);

        // 3. Verificamos que los resultados coincidan con los criterios
        resultados.forEach(articulo -> {
            assertThat(articulo.getCampo3()).isEqualTo(MATCH_C3);
            assertThat(articulo.getCampo4()).isEqualTo(MATCH_C4);
            assertThat(posiblesValoresCampo2).contains(articulo.getCampo2());
        });
    }

    @Test
    void cuandoBuscarConValoresCriteriosDiferentes_entoncesDevuelveListaVacia() {
        // GIVEN (Dados)
        // Usamos valores que sabemos que no coincidirán con ningún registro
        String paramCampo3 = "otro_valor_c3";
        String paramCampo4 = "otro_valor_c4";
        Collection<String> posiblesValoresCampo2 = Arrays.asList(VALUE1, VALUE2);

        // WHEN (Cuando)
        List<MisArticulos> resultados = repository.buscarArticulosPorCriteriosNativos(
            paramCampo3,
            paramCampo4,
            posiblesValoresCampo2
        );

        // THEN (Entonces)
        // La lista debe estar vacía
        assertThat(resultados).isNotNull();
        assertThat(resultados).isEmpty();
    }
}
```

🟢 GUÍA PASO A PASO PARA ACTIVAR EL CICLO COMPLETO DE REINTENTOS SQS → LAMBDA
Incluye:

✔ Activar el trigger SQS en la Lambda
✔ Ajustar permisos IAM
✔ Verificar que la Lambda recibe reintentos
✔ Probar manualmente con un mensaje fallido real

🟦 1. AGREGAR LA COLA SQS DE REINTENTOS COMO TRIGGER
1️⃣ Entra a AWS Console

👉 https://console.aws.amazon.com/lambda

2️⃣ Selecciona tu función Lambda

Busca por nombre, ejemplo:
lambda-msk-sqs-demo-processor

3️⃣ Ve a la pestaña “Configuration”

Luego selecciona Triggers.

4️⃣ Click en “Add trigger”
5️⃣ En la lista, selecciona → SQS

Aquí te aparece un dropdown para elegir la cola.

6️⃣ Selecciona tu cola de reintentos

my-app-ret try-sqs

O el nombre real que tengas.

7️⃣ Batch size

Déjalo en 1 (muy importante para tu código).

8️⃣ Click en “Add”

⚡ Ahora la Lambda procesará mensajes de tu cola Retry SQS.

🟦 2. AGREGAR PERMISOS IAM PARA QUE LA LAMBDA LEA DESDE SQS

Cuando agregas el trigger, AWS pone una policy para que SQS invoque la Lambda,
pero NO pone permisos para que la Lambda pueda consumir SQS.

Eso debes agregarlo tú.

1️⃣ Ve a AWS Console → IAM

👉 https://console.aws.amazon.com/iam

2️⃣ Role de tu Lambda

En tu Lambda, ve a:

Configuration → Permissions → Execution role

Dale click al role.

3️⃣ En ese role → Add permissions → Inline policy
4️⃣ Usa esta JSON policy:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:REGION:ACCOUNT_ID:tu-cola-reintentos"
        }
    ]
}

¿Dónde saco estos valores?

REGION → donde está tu SQS (ej: us-east-1)

ACCOUNT_ID → tu ID de AWS (12 dígitos)

tu-cola-reintentos → nombre exacto de la cola

Puedes ver estos valores así:

✦ En AWS Console → SQS → click en tu cola → “Details”

Aparece:
ARN: arn:aws:sqs:us-east-1:123456789012:my-app-retry-queue

Ese ARN lo pegas en "Resource": ".....".

🟦 3. CONFIRMAR QUE LA LAMBDA RECIBE MENSAJES DESDE SQS

Para verificar que ya todo está conectado:

Paso 1 — Entra a tu cola SQS Retry

👉 SQS → selecciona la cola de reintentos

Paso 2 — Click en Send and receive messages
Paso 3 — En “Message body”, envía un JSON falso (simulación de tu código real)
{
  "openfgaOperations": [
    {
      "data_usr": {"string": "test"},
      "data_num": {"string": "111"},
      "data_tipo": {"string": "G"}
    }
  ]
}

Paso 4 — Click: Send message
Paso 5 — Ve a tu Lambda → “Monitor” → “Logs”

Debe aparecer una ejecución nueva procesando ese mensaje.

Si ves algo como:

INFO processing SQS message id-1


✔ La Lambda ya recibe reintentos desde SQS correctamente.

🟦 4. PROBAR EL FLUJO COMPLETO CON UN EVENTO FALLIDO

Ahora haremos una prueba real:

Prueba simulando error (que envía mensaje a Retry SQS)

Ve a MSK y envía un mensaje malo (o usa la consola de prueba de Lambda)

La Lambda fallará

En tus logs deberías ver:

Sending record to retry queue...


Ve a tu cola Retry
→ verás el mensaje entrar

En unos segundos
→ Lambda lo vuelve a procesar

Si vuelve a fallar
→ El mensaje entra otra vez a Retry

Después de X reintentos
→ Tu código decide enviarlo a la DLQ

🟢 ¿Quieres que te haga ahora un DIAGRAMA resumido de toda tu arquitectura funcionando MSK + LAMBDA + RETRY + DLQ?

Formato ASCII o tipo diagramita “bonito”.

Solo dime: "Sí, dame el diagrama".

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
📄 REQUERIMIENTO DEVOPS – Integración Lambda + SQS Retry/DLQ
✅ Objetivo

Configurar la Lambda:

lambda-msk-sqs-demo-main-lambda

Para integrarse correctamente con:

SQS Retry: lambda-msk-sqs-demo-retry

SQS DLQ: lambda-msk-sqs-demo-dlq

IAM Role de ejecución: lambda-msk-sqs-demo-lambda-role

La Lambda debe:

Recibir mensajes desde la cola retry

Enviar mensajes a retry y a la DLQ

1️⃣ Agregar Trigger SQS a la Lambda

Configurar la cola lambda-msk-sqs-demo-retry como disparador de la Lambda.

Pasos:

Abrir Lambda en AWS Console

Seleccionar lambda-msk-sqs-demo-main-lambda

Ir a Configuration → Triggers

Click en Add trigger

Seleccionar SQS

Elegir la cola → lambda-msk-sqs-demo-retry

2️⃣ Agregar permisos al role lambda-msk-sqs-demo-lambda-role

El role necesita permisos para:

✔ Recibir mensajes
✔ Procesar y eliminar mensajes
✔ Enviar mensajes a Retry y DLQ

Agregar esta Inline Policy:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLambdaToReadRetryQueue",
            "Effect": "Allow",
            "Action": [
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:<REGION>:<ACCOUNT_ID>:lambda-msk-sqs-demo-retry"
        },
        {
            "Sid": "AllowLambdaToSendRetryAndDLQ",
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage"
            ],
            "Resource": [
                "arn:aws:sqs:<REGION>:<ACCOUNT_ID>:lambda-msk-sqs-demo-retry",
                "arn:aws:sqs:<REGION>:<ACCOUNT_ID>:lambda-msk-sqs-demo-dlq"
            ]
        }
    ]
}


Reemplazar <REGION> y <ACCOUNT_ID> por los valores del ambiente.

3️⃣ Verificar policy de invocación de SQS hacia Lambda

Ir a:

Lambda → Configuration → Permissions → Resource-based policy

Debe existir una declaración similar:

{
    "Effect": "Allow",
    "Principal": {
        "Service": "sqs.amazonaws.com"
    },
    "Action": "lambda:InvokeFunction",
    "Resource": "arn:aws:lambda:<REGION>:<ACCOUNT_ID>:function:lambda-msk-sqs-demo-main-lambda",
    "Condition": {
        "ArnLike": {
            "AWS:SourceArn": "arn:aws:sqs:<REGION>:<ACCOUNT_ID>:lambda-msk-sqs-demo-retry"
        }
    }
}

4️⃣ Resultado esperado

Después de aplicar los cambios:

La Lambda podrá procesar mensajes desde Retry

La Lambda podrá enviar mensajes a Retry y DLQ

Flujo final funcionando:

MSK → Lambda → Falla → Retry SQS → Lambda → Falla → DLQ

```
