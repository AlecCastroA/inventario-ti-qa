import unicodedata
from functools import lru_cache
from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import obtener_entorno
from app.models import AccionHistorial, EstadoEquipo, TipoEquipo
from app.repository import EquipoRepository
from app.service import (
    EquipoNoAsignadoError,
    EquipoNoDisponibleError,
    EquipoNoEncontradoError,
    EquipoService,
    EquipoYaDeBajaError,
    SerieDuplicadaError,
)

app = FastAPI(title="Inventario TI", version="0.1.0")

@lru_cache(maxsize=1)
def obtener_repositorio() -> EquipoRepository:
    return EquipoRepository()

def get_service() -> EquipoService:
    return EquipoService(obtener_repositorio())

ServicioDep: TypeAlias = Annotated[EquipoService, Depends(get_service)]

_ERRORES_HTTP = {
    SerieDuplicadaError: (
        status.HTTP_409_CONFLICT,
        "Ya existe un equipo con ese número de serie",
    ),
    EquipoNoEncontradoError: (
        status.HTTP_404_NOT_FOUND,
        "Equipo no encontrado",
    ),
    EquipoNoDisponibleError: (
        status.HTTP_409_CONFLICT,
        "El equipo no está disponible para asignación",
    ),
    EquipoYaDeBajaError: (
        status.HTTP_409_CONFLICT,
        "El equipo ya fue dado de baja",
    ),
    EquipoNoAsignadoError: (
        status.HTTP_409_CONFLICT,
        "El equipo no está asignado",
    ),
}

async def _responder_error_de_negocio(_request: Request, exc: Exception):
    codigo, detalle = _ERRORES_HTTP[type(exc)]
    return JSONResponse(status_code=codigo, content={"detail": detalle})

for _tipo_error in _ERRORES_HTTP:
    app.add_exception_handler(_tipo_error, _responder_error_de_negocio)

def _sin_invisibles(valor: str) -> str:
    limpio = "".join(c for c in valor if unicodedata.category(c) != "Cf").strip()
    if not limpio:
        raise ValueError("El valor no puede estar vacío")
    return limpio

class EquipoCrear(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tipo: TipoEquipo
    marca_modelo: str = Field(min_length=1, max_length=100)
    numero_serie: str = Field(min_length=1, max_length=50)

    @field_validator("marca_modelo", "numero_serie")
    @classmethod
    def sin_invisibles(cls, valor: str) -> str:
        return _sin_invisibles(valor)

class AsignacionCrear(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    usuario: str = Field(min_length=1, max_length=100)

    @field_validator("usuario")
    @classmethod
    def sin_invisibles(cls, valor: str) -> str:
        return _sin_invisibles(valor)

class EquipoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: TipoEquipo
    marca_modelo: str
    numero_serie: str
    estado: EstadoEquipo
    asignado_a: str | None

class EventoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    accion: AccionHistorial
    usuario: str | None


@app.post("/equipos",response_model=EquipoRespuesta,status_code=status.HTTP_201_CREATED,)
def registrar_equipo(datos: EquipoCrear, servicio: ServicioDep):
    return servicio.registrar(datos.tipo, datos.marca_modelo, datos.numero_serie)

@app.get("/equipos", response_model=list[EquipoRespuesta])
def listar_equipos(
    servicio: ServicioDep,
    tipo: TipoEquipo | None = None,
    estado: EstadoEquipo | None = None,
    q: str | None = None,
):
    return servicio.listar(tipo, estado, q)


@app.get("/equipos/{equipo_id}", response_model=EquipoRespuesta)
def obtener_equipo(equipo_id: int, servicio: ServicioDep):
    return servicio.obtener(equipo_id)

@app.post("/equipos/{equipo_id}/asignar", response_model=EquipoRespuesta)
def asignar_equipo(equipo_id: int, datos: AsignacionCrear, servicio: ServicioDep):
    return servicio.asignar(equipo_id, datos.usuario)

@app.post("/equipos/{equipo_id}/baja", response_model=EquipoRespuesta)
def dar_de_baja_equipo(equipo_id: int, servicio: ServicioDep):
    return servicio.dar_de_baja(equipo_id)

@app.get("/salud")
def salud():
    return {"estado": "ok", "entorno": obtener_entorno()}

@app.post("/equipos/{equipo_id}/devolver", response_model=EquipoRespuesta)
def devolver_equipo(equipo_id: int, servicio: ServicioDep):
    return servicio.devolver(equipo_id)

@app.get("/equipos/{equipo_id}/historial", response_model=list[EventoRespuesta])
def historial_equipo(equipo_id: int, servicio: ServicioDep):
    return servicio.historial(equipo_id)