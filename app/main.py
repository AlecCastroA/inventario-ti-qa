from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.config import obtener_entorno
from app.models import EstadoEquipo, TipoEquipo
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

_repositorio = EquipoRepository()


def get_service() -> EquipoService:
    return EquipoService(_repositorio)

ServicioDep: TypeAlias = Annotated[EquipoService, Depends(get_service)]

class EquipoCrear(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tipo: TipoEquipo
    marca_modelo: str = Field(min_length=1, max_length=100)
    numero_serie: str = Field(min_length=1, max_length=50)

class AsignacionCrear(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    usuario: str = Field(min_length=1, max_length=100)

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

    accion: str
    usuario: str | None


@app.post("/equipos", response_model=EquipoRespuesta, status_code=status.HTTP_201_CREATED,)
def registrar_equipo(datos: EquipoCrear, servicio: ServicioDep):
    try:
        return servicio.registrar(
            datos.tipo, datos.marca_modelo, datos.numero_serie
        )
    except SerieDuplicadaError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un equipo con ese número de serie",
        )

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
    try:
        return servicio.obtener(equipo_id)
    except EquipoNoEncontradoError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )

@app.post("/equipos/{equipo_id}/asignar", response_model=EquipoRespuesta)
def asignar_equipo(
    equipo_id: int, datos: AsignacionCrear, servicio: ServicioDep
):
    try:
        return servicio.asignar(equipo_id, datos.usuario)
    except EquipoNoEncontradoError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )
    except EquipoNoDisponibleError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El equipo no está disponible para asignación",
        )

@app.post("/equipos/{equipo_id}/baja", response_model=EquipoRespuesta)
def dar_de_baja_equipo(equipo_id: int, servicio: ServicioDep):
    try:
        return servicio.dar_de_baja(equipo_id)
    except EquipoNoEncontradoError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )
    except EquipoYaDeBajaError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El equipo ya fue dado de baja",
        )

@app.get("/salud")
def salud():
    return {"estado": "ok", "entorno": obtener_entorno()}

@app.post("/equipos/{equipo_id}/devolver", response_model=EquipoRespuesta)
def devolver_equipo(equipo_id: int, servicio: ServicioDep):
    try:
        return servicio.devolver(equipo_id)
    except EquipoNoEncontradoError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )
    except EquipoNoAsignadoError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El equipo no está asignado",
        )

@app.get("/equipos/{equipo_id}/historial", response_model=list[EventoRespuesta])
def historial_equipo(equipo_id: int, servicio: ServicioDep):
    try:
        return servicio.historial(equipo_id)
    except EquipoNoEncontradoError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipo no encontrado",
        )