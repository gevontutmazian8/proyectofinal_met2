"""Datos y reglas de dominio independientes de la base y de la consola."""
from dataclasses import dataclass

TIPOS = ("certificado", "equivalencia", "inscripcion")
PRIORIDADES = ("baja", "media", "alta")
TRANSICIONES = {
    "pendiente": ("en_proceso", "cancelada"),
    "en_proceso": ("resuelta", "cancelada"),
    "resuelta": (),
    "cancelada": (),
}
ESTADOS = tuple(TRANSICIONES)


@dataclass(frozen=True)
class NuevaSolicitud:
    estudiante_id: int
    tipo: str
    prioridad: str
    asunto: str
    descripcion: str
    responsable_id: int | None = None


def validar_texto(valor, mensaje):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(mensaje)


def validar_transicion(actual, destino):
    if destino not in TRANSICIONES.get(actual, ()):
        raise ValueError("Transición inválida")
