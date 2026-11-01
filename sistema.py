"""Servicio de aplicación; conserva el contrato de la consola inicial."""
from repositorio import RepositorioSQLite
from dominio import NuevaSolicitud, TIPOS, PRIORIDADES, ESTADOS, validar_texto, validar_transicion


class Sistema:
    def __init__(self, ruta=":memory:", repositorio=None):
        self.repositorio = repositorio if repositorio is not None else RepositorioSQLite(ruta)

    def cerrar(self):
        self.repositorio.cerrar()

    def registrar_solicitud(self, estudiante_id, tipo, prioridad, asunto, descripcion,
                            responsable_id=None):
        """Adaptador de compatibilidad. Código nuevo: guardar_solicitud(NuevaSolicitud(...))."""
        return self.guardar_solicitud(NuevaSolicitud(
            estudiante_id, tipo, prioridad, asunto, descripcion, responsable_id))

    def operar(self, operacion, **datos):
        acciones = {
            "estudiante": self._estudiante, "responsable": self._responsable,
            "solicitud": self._solicitud, "asignar": self._asignar,
            "estado": self._estado, "consultar": self._consultar,
            "listar": self._listar, "reporte": self._reporte,
        }
        if operacion not in acciones:
            raise ValueError("Operación desconocida")
        return acciones[operacion](datos)

    def _estudiante(self, datos):
        validar_texto(datos.get("nombre"), "Nombre obligatorio")
        email = datos.get("email")
        if not isinstance(email, str) or "@" not in email or not email.strip():
            raise ValueError("Email inválido")
        return self.repositorio.agregar_estudiante(datos["nombre"].strip(), email.strip().lower())

    def _responsable(self, datos):
        validar_texto(datos.get("nombre"), "Nombre obligatorio")
        return self.repositorio.agregar_responsable(datos["nombre"].strip())

    def _solicitud(self, datos):
        nueva = NuevaSolicitud(**{campo: datos.get(campo) for campo in
            ("estudiante_id", "tipo", "prioridad", "asunto", "descripcion", "responsable_id")})
        return self.guardar_solicitud(nueva)

    def guardar_solicitud(self, nueva: NuevaSolicitud):
        if not self.repositorio.existe_estudiante(nueva.estudiante_id):
            raise ValueError("Estudiante inexistente")
        if nueva.tipo not in TIPOS:
            raise ValueError("Tipo inválido")
        if nueva.prioridad not in PRIORIDADES:
            raise ValueError("Prioridad inválida")
        validar_texto(nueva.asunto, "Asunto obligatorio")
        validar_texto(nueva.descripcion, "Descripción obligatoria")
        if nueva.responsable_id is not None:
            if not self.repositorio.existe_responsable(nueva.responsable_id):
                raise ValueError("Responsable inexistente")
        return self.repositorio.agregar_solicitud(nueva)

    def _asignar(self, datos):
        self.repositorio.obtener_solicitud(datos.get("id"))
        if not self.repositorio.existe_responsable(datos.get("responsable_id")):
            raise ValueError("Responsable inexistente")
        self.repositorio.asignar(datos["id"], datos["responsable_id"])

    def _estado(self, datos):
        solicitud = self.repositorio.obtener_solicitud(datos.get("id"))
        validar_transicion(solicitud["estado"], datos.get("estado"))
        self.repositorio.cambiar_estado(datos["id"], datos["estado"])

    def _consultar(self, datos):
        return self.repositorio.obtener_solicitud(datos.get("id"))

    def _listar(self, datos):
        if datos.get("estado") is not None and datos["estado"] not in ESTADOS:
            raise ValueError("Estado inválido")
        if datos.get("prioridad") is not None and datos["prioridad"] not in PRIORIDADES:
            raise ValueError("Prioridad inválida")
        return self.repositorio.listar(datos.get("estado"), datos.get("prioridad"), datos.get("texto"))

    def _reporte(self, datos):
        cantidades = self.repositorio.contar_por_estado()
        resultado = {estado: cantidades.get(estado, 0) for estado in ESTADOS}
        return {"total": sum(resultado.values()), "por_estado": resultado}
