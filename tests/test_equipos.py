import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.repository import EquipoRepository
from app.service import EquipoService


@pytest.fixture
def client():
    repositorio = EquipoRepository()
    app.dependency_overrides[get_service] = lambda: EquipoService(repositorio)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _equipo(**cambios):
    datos = {
        "tipo": "laptop",
        "marca_modelo": "Lenovo ThinkPad T14",
        "numero_serie": "SN-001",
    }
    datos.update(cambios)
    return datos


def test_registrar_equipo_devuelve_201_y_estado_disponible(client):
    respuesta = client.post("/equipos", json=_equipo())
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] == 1
    assert cuerpo["estado"] == "disponible"
    assert cuerpo["asignado_a"] is None


def test_registrar_serie_duplicada_devuelve_409(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.post("/equipos", json=_equipo(numero_serie="sn-001"))
    assert respuesta.status_code == 409


def test_registrar_con_serie_vacia_devuelve_422(client):
    respuesta = client.post("/equipos", json=_equipo(numero_serie="   "))
    assert respuesta.status_code == 422


def test_registrar_con_tipo_invalido_devuelve_422(client):
    respuesta = client.post("/equipos", json=_equipo(tipo="tostadora"))
    assert respuesta.status_code == 422

def test_listar_devuelve_lista_vacia_al_inicio(client):
    respuesta = client.get("/equipos")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_devuelve_todos_los_equipos(client):
    client.post("/equipos", json=_equipo(numero_serie="SN-001"))
    client.post("/equipos", json=_equipo(numero_serie="SN-002"))
    respuesta = client.get("/equipos")
    assert len(respuesta.json()) == 2


def test_filtrar_por_tipo(client):
    client.post("/equipos", json=_equipo(numero_serie="SN-001", tipo="laptop"))
    client.post(
        "/equipos", json=_equipo(numero_serie="SN-002", tipo="impresora")
    )
    respuesta = client.get("/equipos", params={"tipo": "impresora"})
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["tipo"] == "impresora"


def test_filtrar_por_estado(client):
    client.post("/equipos", json=_equipo())
    disponibles = client.get("/equipos", params={"estado": "disponible"})
    de_baja = client.get("/equipos", params={"estado": "baja"})
    assert len(disponibles.json()) == 1
    assert de_baja.json() == []


def test_filtro_con_valor_invalido_devuelve_422(client):
    respuesta = client.get("/equipos", params={"tipo": "tostadora"})
    assert respuesta.status_code == 422


def test_obtener_equipo_por_id(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.get("/equipos/1")
    assert respuesta.status_code == 200
    assert respuesta.json()["numero_serie"] == "SN-001"


def test_obtener_equipo_inexistente_devuelve_404(client):
    respuesta = client.get("/equipos/999")
    assert respuesta.status_code == 404

def test_asignar_equipo_disponible(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.post("/equipos/1/asignar", json={"usuario": "Ana Torres"})
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "asignado"
    assert cuerpo["asignado_a"] == "Ana Torres"


def test_asignar_equipo_ya_asignado_devuelve_409(client):
    client.post("/equipos", json=_equipo())
    client.post("/equipos/1/asignar", json={"usuario": "Ana Torres"})
    respuesta = client.post("/equipos/1/asignar", json={"usuario": "Luis Rojas"})
    assert respuesta.status_code == 409


def test_asignar_equipo_inexistente_devuelve_404(client):
    respuesta = client.post("/equipos/999/asignar", json={"usuario": "Ana Torres"})
    assert respuesta.status_code == 404


def test_asignar_con_usuario_vacio_devuelve_422(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.post("/equipos/1/asignar", json={"usuario": "   "})
    assert respuesta.status_code == 422


def test_filtrar_por_estado_asignado(client):
    client.post("/equipos", json=_equipo(numero_serie="SN-001"))
    client.post("/equipos", json=_equipo(numero_serie="SN-002"))
    client.post("/equipos/1/asignar", json={"usuario": "Ana Torres"})
    respuesta = client.get("/equipos", params={"estado": "asignado"})
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_serie"] == "SN-001"

def test_dar_de_baja_equipo_disponible(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.post("/equipos/1/baja")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "baja"


def test_dar_de_baja_equipo_asignado_libera_al_usuario(client):
    client.post("/equipos", json=_equipo())
    client.post("/equipos/1/asignar", json={"usuario": "Ana Torres"})
    respuesta = client.post("/equipos/1/baja")
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["asignado_a"] is None


def test_dar_de_baja_dos_veces_devuelve_409(client):
    client.post("/equipos", json=_equipo())
    client.post("/equipos/1/baja")
    respuesta = client.post("/equipos/1/baja")
    assert respuesta.status_code == 409


def test_dar_de_baja_equipo_inexistente_devuelve_404(client):
    respuesta = client.post("/equipos/999/baja")
    assert respuesta.status_code == 404


def test_asignar_equipo_de_baja_devuelve_409(client):
    client.post("/equipos", json=_equipo())
    client.post("/equipos/1/baja")
    respuesta = client.post(
        "/equipos/1/asignar", json={"usuario": "Ana Torres"}
    )
    assert respuesta.status_code == 409


def test_filtrar_por_estado_baja(client):
    client.post("/equipos", json=_equipo(numero_serie="SN-001"))
    client.post("/equipos", json=_equipo(numero_serie="SN-002"))
    client.post("/equipos/2/baja")
    respuesta = client.get("/equipos", params={"estado": "baja"})
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_serie"] == "SN-002"

def test_salud_devuelve_ok_y_el_entorno_configurado(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "prueba")
    respuesta = client.get("/salud")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok", "entorno": "prueba"}


def test_salud_usa_desarrollo_por_defecto(client, monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    respuesta = client.get("/salud")
    assert respuesta.json()["entorno"] == "desarrollo"

def test_devolver_equipo_asignado_lo_deja_disponible(client):
    client.post("/equipos", json=_equipo())
    client.post("/equipos/1/asignar", json={"usuario": "Ana Torres"})
    respuesta = client.post("/equipos/1/devolver")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "disponible"
    assert cuerpo["asignado_a"] is None


def test_devolver_equipo_no_asignado_devuelve_409(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.post("/equipos/1/devolver")
    assert respuesta.status_code == 409

def test_historial_registra_el_ciclo_de_un_equipo(client):
    client.post("/equipos", json=_equipo())
    client.post("/equipos/1/asignar", json={"usuario": "Ana Torres"})
    client.post("/equipos/1/devolver")
    respuesta = client.get("/equipos/1/historial")
    assert respuesta.status_code == 200
    acciones = [evento["accion"] for evento in respuesta.json()]
    assert acciones == ["registro", "asignacion", "devolucion"]


def test_historial_de_equipo_inexistente_devuelve_404(client):
    respuesta = client.get("/equipos/999/historial")
    assert respuesta.status_code == 404

def test_buscar_por_texto_en_marca_modelo(client):
    client.post(
        "/equipos",
        json=_equipo(numero_serie="SN-001", marca_modelo="Lenovo ThinkPad"),
    )
    client.post(
        "/equipos",
        json=_equipo(numero_serie="SN-002", marca_modelo="HP LaserJet"),
    )
    respuesta = client.get("/equipos", params={"q": "lenovo"})
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_serie"] == "SN-001"


def test_buscar_por_numero_de_serie_sin_distinguir_mayusculas(client):
    client.post("/equipos", json=_equipo(numero_serie="SN-001"))
    client.post("/equipos", json=_equipo(numero_serie="XY-777"))
    respuesta = client.get("/equipos", params={"q": "xy-7"})
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_serie"] == "XY-777"