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
##tests/test_procesador_tabla1.py
 import pytest
from unittest.mock import Mock
from procesadores.procesador_tabla1 import TABLA1
from services.excepciones import BadRequestError
from utilitarios.constantes import (
    ErroresLiterales,
    OpenFGATipo,
    OpenFGARelacion,
    CuentasValorConstante
)

# ==============================================
# FIXTURES
# ==============================================

@pytest.fixture
def mock_cliente():
    """
    Mock de clienteServicio usado por TABLA1.
    """
    mock = Mock()
    mock._fga_config = {"MODEL_ID": "TEST_MODEL_ID"}
    return mock


@pytest.fixture
def tabla1(monkeypatch, mock_cliente):
    """
    Crea una instancia de TABLA1 con clienteServicio mockeado.
    """
    monkeypatch.setattr(
        "procesadores.procesador_tabla1.clienteServicio",
        lambda: mock_cliente
    )
    return TABLA1()


# ==============================================
# BASE EVENT
# ==============================================

BASE_EVENT = {
    "data_usr": {"string": "user123"},
    "data_num": {"string": "CI100"},
    "data_tipo": {"string": "G"},
    "antigua_data_usr": {"string": "userOld"},
    "antigua_data_num": {"string": "CI999"},
}


# ==============================================
# DELETE
# ==============================================

def test_delete_success(tabla1, mock_cliente):
    mock_cliente.delete_tuple.return_value = "OK"

    result = tabla1.delete(BASE_EVENT)

    assert result == "OK"
    mock_cliente.delete_tuple.assert_called_once()


def test_delete_missing_fields(tabla1):
    event = {"antigua_data_usr": {"string": ""}, "antigua_data_num": {"string": ""}}

    with pytest.raises(BadRequestError) as err:
        tabla1.delete(event)

    assert "usuario:,ci:,tipo:delete" in str(err.value)


# ==============================================
# CREATE
# ==============================================

def test_create_success(tabla1, mock_cliente):
    mock_cliente.write_tuple.return_value = "CREATED"

    result = tabla1.create(BASE_EVENT)

    assert result == "CREATED"
    mock_cliente.write_tuple.assert_called_once()


def test_create_missing_fields(tabla1):
    event = {"data_usr": {"string": ""}, "data_num": {"string": ""}}

    with pytest.raises(BadRequestError):
        tabla1.create(event)


# ==============================================
# CHECK
# ==============================================

def test_check_success(tabla1, mock_cliente):
    mock_cliente.check_tuple.return_value = True

    result = tabla1.check(BASE_EVENT)

    assert result is True
    mock_cliente.check_tuple.assert_called_once()


def test_check_missing_fields(tabla1):
    event = {"antigua_data_usr": {"string": ""}, "antigua_data_num": {"string": ""}}

    with pytest.raises(BadRequestError):
        tabla1.check(event)


# ==============================================
# UPDATE – 3 caminos
# ==============================================

def test_update_case_A_calls_delete(tabla1, mock_cliente):
    """
    Caso A:
    Tipo = GESTOR, tupla existe -> DELETE
    """
    mock_cliente.check_tuple.return_value = True
    mock_cliente.delete_tuple.return_value = "DELETED"

    result = tabla1.update(BASE_EVENT)

    assert result == "DELETED"
    mock_cliente.delete_tuple.assert_called_once()


def test_update_case_B_calls_create(tabla1, mock_cliente):
    """
    Caso B:
    Tipo = SUPER_POWER, tupla NO existe -> CREATE
    """
    event = dict(BASE_EVENT)
    event["data_tipo"]["string"] = CuentasValorConstante.ES_TIPO_SUPER_POWER.value

    mock_cliente.check_tuple.return_value = False
    mock_cliente.write_tuple.return_value = "CREATED"

    result = tabla1.update(event)

    assert result == "CREATED"
    mock_cliente.write_tuple.assert_called_once()


def test_update_case_C_raises(tabla1, mock_cliente):
    """
    Caso C:
    Ninguna condición válida -> ERROR
    """
    event = dict(BASE_EVENT)
    event["data_tipo"]["string"] = "X"

    mock_cliente.check_tuple.return_value = False

    with pytest.raises(BadRequestError):
        tabla1.update(event)


# ==============================================
# _obtener_fga_peticion
# ==============================================

def test_obtener_fga_peticion(tabla1, mock_cliente):
    req = tabla1._obtener_fga_peticion("userABC", "CI777")

    assert req.modelo_autorizacion_id == "TEST_MODEL_ID"
    assert req.tuple_key.relation == OpenFGARelacion.USER_ADMIN_CI
    assert req.tuple_key.user == {OpenFGATipo.USER.value: "userABC"}
    assert req.tuple_key.object == {OpenFGATipo.PROFILE.value: "CI777"}


# ==============================================
# __obtener_tuple_logging_info
# ==============================================

def test_obtener_tuple_logging_info(tabla1):
    msg = tabla1._TABLA1__obtener_tuple_logging_info("u1", "ci1", "delete")

    assert ErroresLiterales.INFORMACION_FALTANTE_TABLA1.value in msg
    assert "usuario:u1,ci:ci1,tipo:delete" in msg


## tests/test_funcion_evento.py
import pytest
from unittest.mock import Mock, patch
from utilitarios.constantes import FuenteEvento, TipoEvento

import utilitarios.funcion_evento as fe


# ==============================================
# TEST obtener_evento_identificador()
# ==============================================

def test_obtener_evento_identificador_usando_fuente_normal():
    event = {
        "fuente": {"string": "TABLA1"},
        "EVENTO_TIPO": {"string": "AC"}
    }

    res = fe.obtener_evento_identificador(event)

    assert res == {"fuente": "TABLA1", "tipo_evento": "AC"}


def test_obtener_evento_identificador_usando_antigua_fuente():
    event = {
        "antigua_fuente": {"string": "TABLA1"},
        "EVENTO_TIPO": {"string": "EL"}
    }

    res = fe.obtener_evento_identificador(event)

    assert res == {"fuente": "TABLA1", "tipo_evento": "EL"}


def test_obtener_evento_identificador_nulos():
    event = {}

    res = fe.obtener_evento_identificador(event)

    assert res == {"fuente": None, "tipo_evento": None}


# ==============================================
# TEST procesar_evento()
# ==============================================

@pytest.fixture
def mock_tabla1(monkeypatch):
    """
    Mockea TABLA1 completo y lo inyecta en la función.
    """
    mock = Mock()
    monkeypatch.setattr(fe, "TABLA1", lambda: mock)
    return mock


def test_procesar_evento_delete(mock_tabla1):
    evento = {}
    mock_tabla1.delete.return_value = "DELETED"

    result = fe.procesar_evento(evento, FuenteEvento.TABLA1, TipoEvento.ELIMINAR)

    assert result == "DELETED"
    mock_tabla1.delete.assert_called_once_with(evento)


def test_procesar_evento_create(mock_tabla1):
    evento = {}
    mock_tabla1.create.return_value = "CREATED"

    result = fe.procesar_evento(evento, FuenteEvento.TABLA1, TipoEvento.CREAR)

    assert result == "CREATED"
    mock_tabla1.create.assert_called_once_with(evento)


def test_procesar_evento_update(mock_tabla1):
    evento = {}
    mock_tabla1.update.return_value = "UPDATED"

    result = fe.procesar_evento(evento, FuenteEvento.TABLA1, TipoEvento.ACTUALIZAR)

    assert result == "UPDATED"
    mock_tabla1.update.assert_called_once_with(evento)


def test_procesar_evento_fuente_no_soportada(mock_tabla1):
    """
    Si pusieras más procesadores en el futuro,
    este test se anticipa a asegurar que TABLA1 solo se usa para la fuente correcta.
    """
    evento = {}

    # No debería llamar nada
    fe.procesar_evento(evento, FuenteEvento.TABLA2, TipoEvento.CREAR)

    mock_tabla1.create.assert_not_called()
    mock_tabla1.update.assert_not_called()
    mock_tabla1.delete.assert_not_called()

##tests/test_conexion_redis.py
import pytest
from unittest.mock import patch, Mock

import utilitarios.conexion_redis as cr


# ==============================================
# FIXTURE PARA RESETEAR CACHE GLOBAL
# ==============================================

@pytest.fixture(autouse=True)
def reset_global():
    cr.redis_cliente = None
    yield
    cr.redis_cliente = None


# ==============================================
# TEST obtener_conexion()
# ==============================================

def test_obtener_conexion_crea_nueva_instancia(monkeypatch):
    fake_pool = Mock()
    fake_redis = Mock()

    monkeypatch.setattr(cr, "ConnectionPool", lambda **kwargs: fake_pool)
    monkeypatch.setattr(cr, "Redis", lambda connection_pool: fake_redis)

    config = Mock()
    config._redis_config = {"REDIS_HOST": "localhost", "REDIS_PORT": 6379}

    conn = cr.obtener_conexion(config)

    assert conn == fake_redis
    assert cr.redis_cliente == fake_redis


def test_obtener_conexion_reutiliza_instancia(monkeypatch):
    fake_pool = Mock()
    fake_redis = Mock()

    monkeypatch.setattr(cr, "ConnectionPool", lambda **kwargs: fake_pool)
    monkeypatch.setattr(cr, "Redis", lambda connection_pool: fake_redis)

    config = Mock()
    config._redis_config = {"REDIS_HOST": "localhost", "REDIS_PORT": 6379}

    first = cr.obtener_conexion(config)
    second = cr.obtener_conexion(config)

    assert first is second  # reutilización
    assert cr.redis_cliente is first


def test_connection_parameters(monkeypatch):
    captured_kwargs = {}

    def fake_pool(**kwargs):
        captured_kwargs.update(kwargs)
        return Mock()

    monkeypatch.setattr(cr, "ConnectionPool", fake_pool)
    monkeypatch.setattr(cr, "Redis", lambda connection_pool: Mock())

    config = Mock()
    config._redis_config = {"REDIS_HOST": "redis.domain", "REDIS_PORT": 9999}

    cr.obtener_conexion(config)

    assert captured_kwargs["host"] == "redis.domain"
    assert captured_kwargs["port"] == 9999
    assert captured_kwargs["decode_responses"] is True

```
