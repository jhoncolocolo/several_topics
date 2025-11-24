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
## test_escribir_o_borrar_tupla_peticion.py
import pytest
from models.escribir_o_borrar_tupla_peticion import (
    TuplaLlave,
    EscribirTuplaPeticion
)
from utilitarios.constantes import OpenFGARelacion, OpenFGATipo


# ============================================================
# FIXTURA BÁSICA (petición completa real)
# ============================================================

@pytest.fixture
def sample_tuple_key():
    return TuplaLlave(
        user={OpenFGATipo.USER.value: "userA"},
        relation=OpenFGARelacion.USER_ADMIN_CI,
        object={OpenFGATipo.PROFILE.value: "obj1"}
    )


@pytest.fixture
def sample_request(sample_tuple_key):
    return EscribirTuplaPeticion(
        tuple_key=sample_tuple_key,
        modelo_autorizacion_id="TEST_MODEL"
    )


# ============================================================
# TEST 1: instanciación de TuplaLlave
# ============================================================

def test_tuple_llave_instantiation():
    key = TuplaLlave(
        user={OpenFGATipo.USER.value: "john"},
        relation=OpenFGARelacion.USER_OWNER_PROFILE,
        object={OpenFGATipo.PROFILE.value: "ABC123"}
    )

    assert key.user == {"user": "john"}
    assert key.relation == OpenFGARelacion.USER_OWNER_PROFILE
    assert key.object == {"profile": "ABC123"}


# ============================================================
# TEST 2: instanciación de EscribirTuplaPeticion
# ============================================================

def test_escribir_tupla_peticion_instantiation(sample_request, sample_tuple_key):
    assert sample_request.modelo_autorizacion_id == "TEST_MODEL"
    assert sample_request.tuple_key == sample_tuple_key


# ============================================================
# TEST 3: guardar_to_dict() devuelve estructura correcta
# ============================================================

def test_guardar_to_dict_structure(sample_request):
    result = sample_request.guardar_to_dict()

    assert "writes" in result
    assert "tuple_keys" in result["writes"]
    assert "modelo_autorizacion_id" in result

    tk = result["writes"]["tuple_keys"][0]

    assert tk["user"] == sample_request.tuple_key.user
    assert tk["relation"] == sample_request.tuple_key.relation
    assert tk["object"] == sample_request.tuple_key.object

    assert result["modelo_autorizacion_id"] == "TEST_MODEL"


# ============================================================
# TEST 4: borrar_to_dict() devuelve misma estructura que guardar_to_dict()
# ============================================================

def test_borrar_to_dict_structure(sample_request):
    result = sample_request.borrar_to_dict()

    assert "writes" in result
    assert "tuple_keys" in result["writes"]

    tk = result["writes"]["tuple_keys"][0]

    assert tk["user"] == sample_request.tuple_key.user
    assert tk["relation"] == sample_request.tuple_key.relation
    assert tk["object"] == sample_request.tuple_key.object


# ============================================================
# TEST 5: parametrizar diferentes entradas
# ============================================================

@pytest.mark.parametrize(
    "user, obj",
    [
        ("user1", "CI001"),
        ("userXYZ", "CI999"),
        ("abc", "12345"),
    ]
)
def test_parametrized_requests(user, obj):
    key = TuplaLlave(
        user={OpenFGATipo.USER.value: user},
        relation=OpenFGARelacion.USER_ADMIN_CI,
        object={OpenFGATipo.PROFILE.value: obj},
    )

    req = EscribirTuplaPeticion(key, modelo_autorizacion_id="MODEL123")

    result = req.guardar_to_dict()

    tk = result["writes"]["tuple_keys"][0]

    assert tk["user"] == {"user": user}
    assert tk["object"] == {"profile": obj}
    assert result["modelo_autorizacion_id"] == "MODEL123"


# ============================================================
# TEST 6: asegurarse que no se retornan referencias mutables
# ============================================================

def test_guardar_to_dict_independencia(sample_request):
    r1 = sample_request.guardar_to_dict()
    r2 = sample_request.guardar_to_dict()

    # modificar r1 NO debe afectar r2
    r1["writes"]["tuple_keys"][0]["user"]["user"] = "MOD"

    assert r2["writes"]["tuple_keys"][0]["user"]["user"] != "MOD"


# ============================================================
# TEST 7: relación es un Enum válido
# ============================================================

def test_relation_is_enum(sample_request):
    assert isinstance(sample_request.tuple_key.relation, OpenFGARelacion)
    assert sample_request.tuple_key.relation.value == "administrator"


## test_cliente_servicio.py
import pytest
from unittest.mock import Mock
import json

from services.cliente_servicio import clienteServicio
from services.excepciones import OpenFGAError
from models.escribir_o_borrar_tupla_peticion import (
    EscribirTuplaPeticion,
    TuplaLlave,
)
from utilitarios.constantes import OpenFGARelacion, OpenFGATipo


# ============================================================
# FIXTURE: parchear configuracion OpenFGA
# ============================================================

@pytest.fixture(autouse=True)
def patch_openfga_config(monkeypatch):
    monkeypatch.setattr(
        "services.cliente_servicio.obtener_configuracion_openfga",
        lambda: {
            "API_URL": "https://fake-fga",
            "STORE_ID": "store123",
            "MODEL_ID": "MODEL_X"
        }
    )


# ============================================================
# FIXTURE: request REALISTA DE EscribirTuplaPeticion
# ============================================================

@pytest.fixture
def fake_request():
    tuple_key = TuplaLlave(
        user={OpenFGATipo.USER.value: "userA"},
        relation=OpenFGARelacion.USER_ADMIN_CI,
        object={OpenFGATipo.PROFILE.value: "obj1"},
    )

    req = EscribirTuplaPeticion(
        tuple_key=tuple_key,
        modelo_autorizacion_id="MODEL_X"
    )

    return req


# ============================================================
# WRITE TUPLE
# ============================================================

def test_write_tuple_ok(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.return_value = Mock(status=200)

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    assert c.write_tuple(fake_request) is True


def test_write_tuple_bad_status(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.return_value = Mock(status=500)

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    assert c.write_tuple(fake_request) is False


def test_write_tuple_exception(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.side_effect = Exception("NETWORK FAIL")

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    with pytest.raises(OpenFGAError):
        c.write_tuple(fake_request)


# ============================================================
# REMOVE TUPLE
# ============================================================

def test_remove_tuple_ok(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.return_value = Mock(status=200)

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    assert c.remove_tuple(fake_request) is True


def test_remove_tuple_bad_status(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.return_value = Mock(status=400)

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    assert c.remove_tuple(fake_request) is False


def test_remove_tuple_exception(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.side_effect = Exception("DELETE ERROR")

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    with pytest.raises(OpenFGAError):
        c.remove_tuple(fake_request)


# ============================================================
# CHECK TUPLE
# ============================================================

def test_comprobar_tupla_allowed_true(monkeypatch, fake_request):
    fake_resp = Mock()
    fake_resp.status = 200
    fake_resp.json.return_value = {"allowed": True}

    fake_http = Mock(request=Mock(return_value=fake_resp))
    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    assert c.comprobar_tupla(fake_request) is True


def test_comprobar_tupla_allowed_false(monkeypatch, fake_request):
    fake_resp = Mock()
    fake_resp.status = 200
    fake_resp.json.return_value = {"allowed": False}

    fake_http = Mock(request=Mock(return_value=fake_resp))
    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    assert c.comprobar_tupla(fake_request) is False


def test_comprobar_tupla_bad_status(monkeypatch, fake_request):
    fake_resp = Mock(status=500)
    fake_http = Mock(request=Mock(return_value=fake_resp))

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    with pytest.raises(OpenFGAError):
        c.comprobar_tupla(fake_request)


def test_comprobar_tupla_exception(monkeypatch, fake_request):
    fake_http = Mock()
    fake_http.request.side_effect = Exception("CHECK ERROR")

    monkeypatch.setattr(
        "services.cliente_servicio.urllib3.PoolManager",
        lambda timeout: fake_http
    )

    c = clienteServicio()
    with pytest.raises(OpenFGAError):
        c.comprobar_tupla(fake_request)

```
