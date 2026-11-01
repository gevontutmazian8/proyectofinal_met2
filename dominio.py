"""Datos de entrada agrupados; no depende de SQLite ni de la consola."""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class NuevaSolicitud:
    estudiante_id: int
    tipo: str
    prioridad: str
    asunto: str
    descripcion: str
    responsable_id: int | None = None

    def como_dict(self):
        return asdict(self)
