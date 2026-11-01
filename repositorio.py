"""Persistencia SQLite separada del servicio."""
import sqlite3


class RepositorioSQLite:
    def __init__(self, ruta=":memory:"):
            self.c = sqlite3.connect(ruta)
            self.c.row_factory = sqlite3.Row
            self.c.execute("PRAGMA foreign_keys = ON")
            self.c.executescript("""
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
        self.c.close()

    def ejecutar(self, sql, parametros=()):
        return self.c.execute(sql, parametros)

    def __enter__(self):
        self.c.__enter__()
        return self

    def __exit__(self, *args):
        return self.c.__exit__(*args)
