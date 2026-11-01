"""Prototipo didáctico creado para el TPI; datos exclusivamente sintéticos."""
import sqlite3
from repositorio import RepositorioSQLite


def validar_texto(valor, mensaje):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(mensaje)


class Sistema:
    def __init__(self, ruta=":memory:", repositorio=None):
        self.repositorio = repositorio if repositorio is not None else RepositorioSQLite(ruta)

    def cerrar(self):
        self.repositorio.cerrar()

    def registrar_solicitud(self, estudiante_id, tipo, prioridad, asunto, descripcion,
                            responsable_id=None):
        return self.operar("solicitud", estudiante_id=estudiante_id, tipo=tipo,
                           prioridad=prioridad, asunto=asunto, descripcion=descripcion,
                           responsable_id=responsable_id)

    def operar(self, operacion, **datos):
        acciones = {
            "estudiante": self._estudiante,
            "responsable": self._responsable,
            "solicitud": self._solicitud,
            "asignar": self._asignar,
            "estado": self._estado,
            "consultar": self._consultar,
            "listar": self._listar,
            "reporte": self._reporte,
        }
        if operacion not in acciones:
            raise ValueError("Operación desconocida")
        return acciones[operacion](datos)

    def _estudiante(self, datos):
        validar_texto(datos.get('nombre'), 'Nombre obligatorio')
        if not isinstance(datos.get('email'), str) or '@' not in datos['email'] or (not datos['email'].strip()):
            raise ValueError('Email inválido')
        try:
            with self.repositorio:
                r = self.repositorio.ejecutar('INSERT INTO estudiantes(nombre,email) VALUES (?,?)', (datos['nombre'].strip(), datos['email'].strip().lower()))
            return r.lastrowid
        except sqlite3.IntegrityError as exc:
            raise ValueError('Email ya registrado') from exc

    def _responsable(self, datos):
        validar_texto(datos.get('nombre'), 'Nombre obligatorio')
        with self.repositorio:
            r = self.repositorio.ejecutar('INSERT INTO responsables(nombre) VALUES (?)', (datos['nombre'].strip(),))
        return r.lastrowid

    def _solicitud(self, datos):
        if not self.repositorio.ejecutar('SELECT id FROM estudiantes WHERE id=?', (datos.get('estudiante_id'),)).fetchone():
            raise ValueError('Estudiante inexistente')
        if datos.get('tipo') not in ('certificado', 'equivalencia', 'inscripcion'):
            raise ValueError('Tipo inválido')
        if datos.get('prioridad') not in ('baja', 'media', 'alta'):
            raise ValueError('Prioridad inválida')
        if not isinstance(datos.get('asunto'), str) or not datos['asunto'].strip():
            raise ValueError('Asunto obligatorio')
        if not isinstance(datos.get('descripcion'), str) or not datos['descripcion'].strip():
            raise ValueError('Descripción obligatoria')
        if datos.get('responsable_id') is not None:
            if not self.repositorio.ejecutar('SELECT id FROM responsables WHERE id=?', (datos['responsable_id'],)).fetchone():
                raise ValueError('Responsable inexistente')
        with self.repositorio:
            r = self.repositorio.ejecutar("INSERT INTO solicitudes\n                    (estudiante_id,tipo,prioridad,asunto,descripcion,estado,responsable_id)\n                    VALUES (?,?,?,?,?,'pendiente',?)", (datos['estudiante_id'], datos['tipo'], datos['prioridad'], datos['asunto'].strip(), datos['descripcion'].strip(), datos.get('responsable_id')))
        return r.lastrowid

    def _asignar(self, datos):
        if not self.repositorio.ejecutar('SELECT id FROM solicitudes WHERE id=?', (datos.get('id'),)).fetchone():
            raise ValueError('Solicitud inexistente')
        if not self.repositorio.ejecutar('SELECT id FROM responsables WHERE id=?', (datos.get('responsable_id'),)).fetchone():
            raise ValueError('Responsable inexistente')
        with self.repositorio:
            self.repositorio.ejecutar('UPDATE solicitudes SET responsable_id=? WHERE id=?', (datos['responsable_id'], datos['id']))
        return None

    def _estado(self, datos):
        r = self.repositorio.ejecutar('SELECT * FROM solicitudes WHERE id=?', (datos.get('id'),)).fetchone()
        if r is None:
            raise ValueError('Solicitud inexistente')
        if not (r['estado'] == 'pendiente' and datos.get('estado') in ('en_proceso', 'cancelada') or (r['estado'] == 'en_proceso' and datos.get('estado') in ('resuelta', 'cancelada'))):
            raise ValueError('Transición inválida')
        with self.repositorio:
            self.repositorio.ejecutar('UPDATE solicitudes SET estado=? WHERE id=?', (datos['estado'], datos['id']))
        return None

    def _consultar(self, datos):
        r = self.repositorio.ejecutar('SELECT * FROM solicitudes WHERE id=?', (datos.get('id'),)).fetchone()
        if r is None:
            raise ValueError('Solicitud inexistente')
        return dict(r)

    def _listar(self, datos):
        q = 'SELECT * FROM solicitudes WHERE 1=1'
        p = []
        if datos.get('estado') is not None:
            if datos['estado'] not in ('pendiente', 'en_proceso', 'resuelta', 'cancelada'):
                raise ValueError('Estado inválido')
            q += ' AND estado=?'
            p.append(datos['estado'])
        if datos.get('prioridad') is not None:
            if datos['prioridad'] not in ('baja', 'media', 'alta'):
                raise ValueError('Prioridad inválida')
            q += ' AND prioridad=?'
            p.append(datos['prioridad'])
        if datos.get('texto') is not None:
            q += ' AND instr(lower(asunto),lower(?)) > 0'
            p.append(datos['texto'])
        return [dict(r) for r in self.repositorio.ejecutar(q + ' ORDER BY id', p)]

    def _reporte(self, datos):
        filas = self.repositorio.ejecutar('SELECT estado, COUNT(*) AS cantidad FROM solicitudes GROUP BY estado').fetchall()
        resultado = {'pendiente': 0, 'en_proceso': 0, 'resuelta': 0, 'cancelada': 0}
        for r in filas:
            resultado[r['estado']] = r['cantidad']
        return {'total': sum(resultado.values()), 'por_estado': resultado}
