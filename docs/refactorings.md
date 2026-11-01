# Refactorings verificables

Las cuatro transformaciones se hicieron en commits reales, en el orden del historial. Las pruebas preceden a los cambios y se repiten por hito. Los fragmentos siguientes se extraen del código; cuando son parciales se indica su rango. No se alteraron los registros históricos para aparentar trabajo previo.

## R1 - Extract Method y validación compartida

CS01, CS02 y parte de CS07. Commit 32d2492. Se dividió el despachador en operaciones y se extrajo la validación repetida del nombre. SRP y legibilidad: cada caso de uso se inspecciona por separado. La interfaz operar y los errores permanecieron. Ver 02_extract_method.txt: 29 pruebas aprobadas.

versiones/inicial/sistema.py, líneas 31-45.

```python
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
```
sistema.py, líneas 19-28.

```python
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
```
dominio.py, líneas 25-27.

```python
def validar_texto(valor, mensaje):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(mensaje)
```

## R2 - Move Method / reubicación de persistencia

CS03 y CS08. Commit 1cfd75c: conexión, esquema y transacciones se movieron al repositorio. El registro 03_move_method.txt conserva 29 aprobadas. La revisión detectó que el servicio todavía contenía SQL; a379c39 completó el encapsulamiento con métodos semánticos. Esa diferencia se declara para no atribuir al primer paso una separación que todavía no tenía. SRP y DIP parcial.

versiones/inicial/sistema.py, líneas 6-20.

```python
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
```
repositorio.py, líneas 42-47.

```python
    def agregar_solicitud(self, nueva):
        return self._insertar("""INSERT INTO solicitudes
            (estudiante_id,tipo,prioridad,asunto,descripcion,estado,responsable_id)
            VALUES (?,?,?,?,?,'pendiente',?)""",
            (nueva.estudiante_id, nueva.tipo, nueva.prioridad,
             nueva.asunto.strip(), nueva.descripcion.strip(), nueva.responsable_id))
```
sistema.py, líneas 7-8.

```python
    def __init__(self, ruta=":memory:", repositorio=None):
        self.repositorio = repositorio if repositorio is not None else RepositorioSQLite(ruta)
```

## R3 - Introduce Parameter Object

CS04. Commit b5eb55f. NuevaSolicitud reúne los seis datos de una solicitud; guardar_solicitud recibe ese objeto. La API posicional original se conserva como adaptador, por lo que la simplificación no exige romper clientes. No se presenta como eliminación total de la firma larga. Registro 04_parameter_object.txt: 29 aprobadas. La prueba adicional test_objeto_parametros comprueba la nueva vía.

versiones/inicial/sistema.py, líneas 25-29.

```python
    def registrar_solicitud(self, estudiante_id, tipo, prioridad, asunto, descripcion,
                            responsable_id=None):
        return self.operar("solicitud", estudiante_id=estudiante_id, tipo=tipo,
                           prioridad=prioridad, asunto=asunto, descripcion=descripcion,
                           responsable_id=responsable_id)
```
dominio.py, líneas 16-22.

```python
class NuevaSolicitud:
    estudiante_id: int
    tipo: str
    prioridad: str
    asunto: str
    descripcion: str
    responsable_id: int | None = None
```
sistema.py, líneas 46-58.

```python
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
```

## R4 - Decompose Conditional y reglas separadas

CS05 y CS06; completa CS03, CS07 y CS08. Commit a379c39. La condición compuesta se reemplazó por una consulta a TRANSICIONES, con catálogos compartidos. La creación del repositorio también materializa Extract Class. Se preservan exactamente las cuatro transiciones permitidas. OCP localizado: cambia la tabla, no el algoritmo. Registro 05_separar_reglas.txt: 29 aprobadas; la revisión posterior recorre los 16 pares.

versiones/inicial/sistema.py, líneas 79-89.

```python
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
```
dominio.py, tabla de transiciones.

```python
TRANSICIONES = {
    "pendiente": ("en_proceso", "cancelada"),
    "en_proceso": ("resuelta", "cancelada"),
    "resuelta": (),
    "cancelada": (),
}
ESTADOS = tuple(TRANSICIONES)
```
dominio.py, líneas 30-32.

```python
def validar_transicion(actual, destino):
    if destino not in TRANSICIONES.get(actual, ()):
        raise ValueError("Transición inválida")
```
