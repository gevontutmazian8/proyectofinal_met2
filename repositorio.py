"""SQLite: esquema, consultas y transacciones de una operación."""
import sqlite3


class RepositorioSQLite:
    def __init__(self, ruta=":memory:"):
        self.conexion = sqlite3.connect(ruta)
        self.conexion.row_factory = sqlite3.Row
        self.conexion.execute("PRAGMA foreign_keys = ON")
        self.conexion.executescript("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
        CREATE TABLE IF NOT EXISTS responsables (
            id INTEGER PRIMARY KEY, nombre TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY, estudiante_id INTEGER NOT NULL REFERENCES estudiantes(id),
            tipo TEXT NOT NULL, prioridad TEXT NOT NULL, asunto TEXT NOT NULL,
            descripcion TEXT NOT NULL, estado TEXT NOT NULL,
            responsable_id INTEGER REFERENCES responsables(id));
        """)

    def cerrar(self):
        self.conexion.close()

    def agregar_estudiante(self, nombre, email):
        try:
            return self._insertar("INSERT INTO estudiantes(nombre,email) VALUES (?,?)", (nombre, email))
        except sqlite3.IntegrityError as error:
            raise ValueError("Email ya registrado") from error

    def agregar_responsable(self, nombre):
        return self._insertar("INSERT INTO responsables(nombre) VALUES (?)", (nombre,))

    def existe_estudiante(self, identificador):
        fila = self.conexion.execute("SELECT id FROM estudiantes WHERE id=?", (identificador,)).fetchone()
        return fila is not None

    def existe_responsable(self, identificador):
        fila = self.conexion.execute("SELECT id FROM responsables WHERE id=?", (identificador,)).fetchone()
        return fila is not None

    def agregar_solicitud(self, nueva):
        return self._insertar("""INSERT INTO solicitudes
            (estudiante_id,tipo,prioridad,asunto,descripcion,estado,responsable_id)
            VALUES (?,?,?,?,?,'pendiente',?)""",
            (nueva.estudiante_id, nueva.tipo, nueva.prioridad,
             nueva.asunto.strip(), nueva.descripcion.strip(), nueva.responsable_id))

    def obtener_solicitud(self, identificador):
        fila = self.conexion.execute("SELECT * FROM solicitudes WHERE id=?", (identificador,)).fetchone()
        if fila is None:
            raise ValueError("Solicitud inexistente")
        return dict(fila)

    def asignar(self, identificador, responsable_id):
        with self.conexion:
            self.conexion.execute("UPDATE solicitudes SET responsable_id=? WHERE id=?", (responsable_id, identificador))

    def cambiar_estado(self, identificador, estado):
        with self.conexion:
            self.conexion.execute("UPDATE solicitudes SET estado=? WHERE id=?", (estado, identificador))

    def listar(self, estado=None, prioridad=None, texto=None):
        consulta = "SELECT * FROM solicitudes WHERE 1=1"
        parametros = []
        if estado is not None:
            consulta += " AND estado=?"
            parametros.append(estado)
        if prioridad is not None:
            consulta += " AND prioridad=?"
            parametros.append(prioridad)
        if texto is not None:
            consulta += " AND instr(lower(asunto),lower(?)) > 0"
            parametros.append(texto)
        return [dict(fila) for fila in self.conexion.execute(consulta + " ORDER BY id", parametros)]

    def contar_por_estado(self):
        filas = self.conexion.execute("SELECT estado,COUNT(*) FROM solicitudes GROUP BY estado").fetchall()
        return dict(filas)

    def _insertar(self, consulta, parametros):
        with self.conexion:
            cursor = self.conexion.execute(consulta, parametros)
        return cursor.lastrowid
