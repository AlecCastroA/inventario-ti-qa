from app.models import (
    AccionHistorial,
    Equipo,
    EstadoEquipo,
    EventoHistorial,
    TipoEquipo,
)
from app.repository import EquipoRepository


class SerieDuplicadaError(Exception):
    """Ya existe un equipo con ese número de serie."""

class EquipoNoEncontradoError(Exception):
    """No existe un equipo con ese ID."""

class EquipoNoDisponibleError(Exception):
    """El equipo no está disponible para asignarse."""

class EquipoYaDeBajaError(Exception):
    """El equipo ya fue dado de baja."""

class EquipoNoAsignadoError(Exception):
    """El equipo no está asignado."""

def _coincide_tipo(equipo: Equipo, tipo: TipoEquipo | None) -> bool:
    return tipo is None or equipo.tipo == tipo

def _coincide_estado(equipo: Equipo, estado: EstadoEquipo | None) -> bool:
    return estado is None or equipo.estado == estado

def _coincide_texto(equipo: Equipo, q: str | None) -> bool:
    if not q:
        return True
    texto = q.strip().lower()
    return (
        texto in equipo.marca_modelo.lower()
        or texto in equipo.numero_serie.lower()
    )

class EquipoService:
    """Reglas de negocio del inventario."""

    def __init__(self, repositorio: EquipoRepository) -> None:
        self._repo = repositorio

    def registrar(
        self, tipo: TipoEquipo, marca_modelo: str, numero_serie: str
    ) -> Equipo:
        if self._repo.obtener_por_serie(numero_serie) is not None:
            raise SerieDuplicadaError(numero_serie)
        equipo = self._repo.agregar(tipo, marca_modelo, numero_serie)
        self._repo.registrar_evento(equipo.id, AccionHistorial.REGISTRO)
        return equipo

    def listar(
        self,
        tipo: TipoEquipo | None = None,
        estado: EstadoEquipo | None = None,
        q: str | None = None,
    ) -> list[Equipo]:
        return [
            equipo
            for equipo in self._repo.listar()
            if _coincide_tipo(equipo, tipo)
            and _coincide_estado(equipo, estado)
            and _coincide_texto(equipo, q)
        ]

    def obtener(self, equipo_id: int) -> Equipo:
        equipo = self._repo.obtener(equipo_id)
        if equipo is None:
            raise EquipoNoEncontradoError(equipo_id)
        return equipo

    def asignar(self, equipo_id: int, usuario: str) -> Equipo:
        equipo = self.obtener(equipo_id)
        if equipo.estado != EstadoEquipo.DISPONIBLE:
            raise EquipoNoDisponibleError(equipo.estado.value)
        equipo.estado = EstadoEquipo.ASIGNADO
        equipo.asignado_a = usuario
        self._repo.registrar_evento(equipo.id, AccionHistorial.ASIGNACION, usuario)
        return self._repo.actualizar(equipo)

    def dar_de_baja(self, equipo_id: int) -> Equipo:
        equipo = self.obtener(equipo_id)
        if equipo.estado == EstadoEquipo.BAJA:
            raise EquipoYaDeBajaError(equipo_id)
        usuario = equipo.asignado_a
        equipo.estado = EstadoEquipo.BAJA
        equipo.asignado_a = None
        self._repo.registrar_evento(equipo.id, AccionHistorial.BAJA, usuario)
        return self._repo.actualizar(equipo)

    def devolver(self, equipo_id: int) -> Equipo:
        equipo = self.obtener(equipo_id)
        if equipo.estado != EstadoEquipo.ASIGNADO:
            raise EquipoNoAsignadoError(equipo.estado.value)
        usuario = equipo.asignado_a
        equipo.estado = EstadoEquipo.DISPONIBLE
        equipo.asignado_a = None
        self._repo.registrar_evento(equipo.id, AccionHistorial.DEVOLUCION, usuario)
        return self._repo.actualizar(equipo)

    def historial(self, equipo_id: int) -> list[EventoHistorial]:
        self.obtener(equipo_id)
        return self._repo.historial(equipo_id)