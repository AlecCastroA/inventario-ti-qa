from app.models import Equipo, EventoHistorial, TipoEquipo


class EquipoRepository:
    def __init__(self) -> None:
        self._equipos: dict[int, Equipo] = {}
        self._siguiente_id = 1
        self._historial: dict[int, list[EventoHistorial]] = {}

    def agregar(
        self, tipo: TipoEquipo, marca_modelo: str, numero_serie: str
    ) -> Equipo:
        equipo = Equipo(
            id=self._siguiente_id,
            tipo=tipo,
            marca_modelo=marca_modelo,
            numero_serie=numero_serie,
        )
        self._equipos[equipo.id] = equipo
        self._siguiente_id += 1
        return equipo

    def obtener(self, equipo_id: int) -> Equipo | None:
        return self._equipos.get(equipo_id)

    def obtener_por_serie(self, numero_serie: str) -> Equipo | None:
        for equipo in self._equipos.values():
            if equipo.numero_serie.lower() == numero_serie.lower():
                return equipo
        return None

    def listar(self) -> list[Equipo]:
        return list(self._equipos.values())

    def actualizar(self, equipo: Equipo) -> Equipo:
        self._equipos[equipo.id] = equipo
        return equipo

    def registrar_evento(
        self, equipo_id: int, accion: str, usuario: str | None = None
    ) -> None:
        self._historial.setdefault(equipo_id, []).append(
            EventoHistorial(accion, usuario)
        )

    def historial(self, equipo_id: int) -> list[EventoHistorial]:
        return list(self._historial.get(equipo_id, []))