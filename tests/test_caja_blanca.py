import pytest

from app.models import EstadoEquipo, TipoEquipo
from app.repository import EquipoRepository
from app.service import (
    EquipoNoAsignadoError,
    EquipoNoEncontradoError,
    EquipoService,
)


@pytest.fixture
def servicio():
    return EquipoService(EquipoRepository())


def test_cb01_listar_con_los_tres_filtros_a_la_vez(servicio):
    a = servicio.registrar(TipoEquipo.LAPTOP, "Lenovo ThinkPad", "SN-001")
    servicio.registrar(TipoEquipo.LAPTOP, "Lenovo IdeaPad", "SN-002")
    servicio.registrar(TipoEquipo.IMPRESORA, "Lenovo Printer", "SN-003")
    servicio.asignar(a.id, "Ana Torres")
    resultado = servicio.listar(TipoEquipo.LAPTOP, EstadoEquipo.ASIGNADO, "think")
    assert [e.id for e in resultado] == [a.id]


def test_cb02_baja_de_equipo_asignado_registra_al_usuario_previo(servicio):
    equipo = servicio.registrar(TipoEquipo.ROUTER, "TP-Link", "SN-010")
    servicio.asignar(equipo.id, "Luis Rojas")
    servicio.dar_de_baja(equipo.id)
    ultimo = servicio.historial(equipo.id)[-1]
    assert (ultimo.accion, ultimo.usuario) == ("baja", "Luis Rojas")


def test_cb03_devolver_cubre_equipo_no_asignado_y_asignado(servicio):
    equipo = servicio.registrar(TipoEquipo.LAPTOP, "Dell Latitude", "SN-020")
    with pytest.raises(EquipoNoAsignadoError):
        servicio.devolver(equipo.id)
    servicio.asignar(equipo.id, "Ana Torres")
    assert servicio.devolver(equipo.id).estado == EstadoEquipo.DISPONIBLE


def test_cb04_historial_de_equipo_inexistente_lanza_error(servicio):
    with pytest.raises(EquipoNoEncontradoError):
        servicio.historial(999)