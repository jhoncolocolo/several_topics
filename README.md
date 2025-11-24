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
##  src\procesadores\procesador_tabla1.py
from models.escribir_o_borrar_tupla_peticion import TuplaLlave, EscribirTuplaPeticion
from utilitarios.constantes import OpenFGARelacion, OpenFGATipo, ErroresLiterales,CuentasValorConstante
from services.cliente_servicio import clienteServicio
from services.excepciones import BadRequestError
import json

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class TABLA1:
    _cliente_servicio = None

    def __init__(self):
        TABLA1._cliente_servicio = clienteServicio()

    def delete(self, event: dict):
        user = event.get('antigua_data_usr', {}).get('string').strip()
        ci = event.get('antigua_data_num', {}).get('string').strip()

        if not user or not ci:
            raise BadRequestError(self.__obtener_tuple_logging_info(user,ci,'delete'))

        request = self._obtener_fga_peticion(user, ci)
        return TABLA1._cliente_servicio.delete_tuple(request=request)

    def create(self, event: dict):
        user = event.get('data_usr', {}).get('string').strip()
        ci = event.get('data_num', {}).get('string').strip()

        if not user or not ci:
           raise BadRequestError(self.__obtener_tuple_logging_info(user,ci,'create'))

        request = self._obtener_fga_peticion(user, ci)
        return TABLA1._cliente_servicio.write_tuple(request=request)

    def check(self, event: dict):
        user = event.get('antigua_data_usr', {}).get('string').strip()
        ci = event.get('antigua_data_num', {}).get('string').strip()

        if not user or not ci:
            raise BadRequestError(self.__obtener_tuple_logging_info(user,ci,'verificar'))

        request = self._obtener_fga_peticion(user, ci)
        exists = TABLA1._cliente_servicio.check_tuple(request=request)
        return exists

    def update(self, event: dict):
        user_type = event.get('data_tipo', {}).get('string').strip()
        doesTupleExists = self.check(event)
        if user_type == CuentasValorConstante.ES_TIPO_GESTOR and doesTupleExists:
            isTupleDeleted = self.delete(event)
            return isTupleDeleted
        elif user_type == CuentasValorConstante.ES_TIPO_SUPER_POWER and not doesTupleExists:
            isTupleCreated = self.create(event)
            return isTupleCreated
        else:
            raise BadRequestError(f"{ErroresLiterales.NO_ACTUALIZADO.value}{json.dumps(event)}-existeTupla{doesTupleExists}")


    def _obtener_fga_peticion(self, user: str, ci: str):
        _user = {OpenFGATipo.USER.value: user}
        _object = {OpenFGATipo.PROFILE.value: ci}
        TUPLA_LLAVE = TuplaLlave(user=_user, relation=OpenFGARelacion.USER_ADMIN_CI, object=_object)
        request = EscribirTuplaPeticion(tuple_key= TUPLA_LLAVE, modelo_autorizacion_id= self._cliente_servicio._fga_config['MODEL_ID'])
        return request
    
    def __obtener_tuple_logging_info(self,usuario:str,ci:str,type:str):
        return f"{ErroresLiterales.INFORMACION_FALTANTE_TABLA1.value}usuario:{usuario},ci:{ci},tipo:{type}"

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
