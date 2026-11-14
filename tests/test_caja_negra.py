def _equipo(**cambios):
    datos = {
        "tipo": "laptop",
        "marca_modelo": "Lenovo ThinkPad T14",
        "numero_serie": "SN-001",
    }
    datos.update(cambios)
    return datos


def test_cn01_serie_de_50_caracteres_es_valida(client):
    respuesta = client.post("/equipos", json=_equipo(numero_serie="S" * 50))
    assert respuesta.status_code == 201


def test_cn02_serie_de_51_caracteres_es_rechazada(client):
    respuesta = client.post("/equipos", json=_equipo(numero_serie="S" * 51))
    assert respuesta.status_code == 422


def test_cn03_usuario_de_101_caracteres_es_rechazado(client):
    client.post("/equipos", json=_equipo())
    respuesta = client.post("/equipos/1/asignar", json={"usuario": "U" * 101})
    assert respuesta.status_code == 422


def test_cn04_busqueda_con_solo_espacios_devuelve_todos(client):
    client.post("/equipos", json=_equipo(numero_serie="SN-001"))
    client.post("/equipos", json=_equipo(numero_serie="SN-002"))
    respuesta = client.get("/equipos", params={"q": "   "})
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_cn05_entorno_invalido_usa_desarrollo(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "otro")
    respuesta = client.get("/salud")
    assert respuesta.json()["entorno"] == "desarrollo"