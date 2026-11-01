"""Prototipo didáctico creado para el TPI; datos exclusivamente sintéticos."""
import sqlite3


class Sistema:
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

    def registrar_solicitud(self, estudiante_id, tipo, prioridad, asunto, descripcion,
                            responsable_id=None):
        return self.operar("solicitud", estudiante_id=estudiante_id, tipo=tipo,
                           prioridad=prioridad, asunto=asunto, descripcion=descripcion,
                           responsable_id=responsable_id)

    def operar(self, op, **d):
        if op == "estudiante":
            if not isinstance(d.get("nombre"), str) or not d["nombre"].strip():
                raise ValueError("Nombre obligatorio")
            if not isinstance(d.get("email"), str) or "@" not in d["email"] or not d["email"].strip():
                raise ValueError("Email inválido")
            try:
                with self.c:
                    r = self.c.execute("INSERT INTO estudiantes(nombre,email) VALUES (?,?)",
                                       (d["nombre"].strip(), d["email"].strip().lower()))
                return r.lastrowid
            except sqlite3.IntegrityError as exc:
                raise ValueError("Email ya registrado") from exc
        elif op == "responsable":
            if not isinstance(d.get("nombre"), str) or not d["nombre"].strip():
                raise ValueError("Nombre obligatorio")
            with self.c:
                r = self.c.execute("INSERT INTO responsables(nombre) VALUES (?)", (d["nombre"].strip(),))
            return r.lastrowid
        elif op == "solicitud":
            if not self.c.execute("SELECT id FROM estudiantes WHERE id=?", (d.get("estudiante_id"),)).fetchone():
                raise ValueError("Estudiante inexistente")
            if d.get("tipo") not in ("certificado", "equivalencia", "inscripcion"):
                raise ValueError("Tipo inválido")
            if d.get("prioridad") not in ("baja", "media", "alta"):
                raise ValueError("Prioridad inválida")
            if not isinstance(d.get("asunto"), str) or not d["asunto"].strip():
                raise ValueError("Asunto obligatorio")
            if not isinstance(d.get("descripcion"), str) or not d["descripcion"].strip():
                raise ValueError("Descripción obligatoria")
            if d.get("responsable_id") is not None:
                if not self.c.execute("SELECT id FROM responsables WHERE id=?", (d["responsable_id"],)).fetchone():
                    raise ValueError("Responsable inexistente")
            with self.c:
                r = self.c.execute("""INSERT INTO solicitudes
                    (estudiante_id,tipo,prioridad,asunto,descripcion,estado,responsable_id)
                    VALUES (?,?,?,?,?,'pendiente',?)""",
                    (d["estudiante_id"], d["tipo"], d["prioridad"], d["asunto"].strip(),
                     d["descripcion"].strip(), d.get("responsable_id")))
            return r.lastrowid
        elif op == "asignar":
            if not self.c.execute("SELECT id FROM solicitudes WHERE id=?", (d.get("id"),)).fetchone():
                raise ValueError("Solicitud inexistente")
            if not self.c.execute("SELECT id FROM responsables WHERE id=?", (d.get("responsable_id"),)).fetchone():
                raise ValueError("Responsable inexistente")
            with self.c:
                self.c.execute("UPDATE solicitudes SET responsable_id=? WHERE id=?", (d["responsable_id"], d["id"]))
            return None
        elif op == "estado":
            r = self.c.execute("SELECT * FROM solicitudes WHERE id=?", (d.get("id"),)).fetchone()
            if r is None:
                raise ValueError("Solicitud inexistente")
            if not ((r["estado"] == "pendiente" and d.get("estado") in ("en_proceso", "cancelada"))
                    or (r["estado"] == "en_proceso" and d.get("estado") in ("resuelta", "cancelada"))):
                raise ValueError("Transición inválida")
            with self.c:
                self.c.execute("UPDATE solicitudes SET estado=? WHERE id=?", (d["estado"], d["id"]))
            return None
        elif op == "consultar":
            r = self.c.execute("SELECT * FROM solicitudes WHERE id=?", (d.get("id"),)).fetchone()
            if r is None:
                raise ValueError("Solicitud inexistente")
            return dict(r)
        elif op == "listar":
            q = "SELECT * FROM solicitudes WHERE 1=1"
            p = []
            if d.get("estado") is not None:
                if d["estado"] not in ("pendiente", "en_proceso", "resuelta", "cancelada"):
                    raise ValueError("Estado inválido")
                q += " AND estado=?"
                p.append(d["estado"])
            if d.get("prioridad") is not None:
                if d["prioridad"] not in ("baja", "media", "alta"):
                    raise ValueError("Prioridad inválida")
                q += " AND prioridad=?"
                p.append(d["prioridad"])
            if d.get("texto") is not None:
                # Búsqueda literal, sin interpretar comodines SQL.
                q += " AND instr(lower(asunto),lower(?)) > 0"
                p.append(d["texto"])
            return [dict(r) for r in self.c.execute(q + " ORDER BY id", p)]
        elif op == "reporte":
            filas = self.c.execute("SELECT estado, COUNT(*) AS cantidad FROM solicitudes GROUP BY estado").fetchall()
            resultado = {"pendiente": 0, "en_proceso": 0, "resuelta": 0, "cancelada": 0}
            for r in filas:
                resultado[r["estado"]] = r["cantidad"]
            return {"total": sum(resultado.values()), "por_estado": resultado}
        raise ValueError("Operación desconocida")
