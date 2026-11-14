from dataclasses import dataclass
from enum import Enum


class TipoEquipo(str, Enum):
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    IMPRESORA = "impresora"
    ROUTER = "router"
    ACCESS_POINT = "access_point"
    OTRO = "otro"


class EstadoEquipo(str, Enum):
    DISPONIBLE = "disponible"
    ASIGNADO = "asignado"
    BAJA = "baja"


@dataclass
class Equipo:
    id: int
    tipo: TipoEquipo
    marca_modelo: str
    numero_serie: str
    estado: EstadoEquipo = EstadoEquipo.DISPONIBLE
    asignado_a: str | None = None

@dataclass
class EventoHistorial:
    accion: str
    usuario: str | None = None