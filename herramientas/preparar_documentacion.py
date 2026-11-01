"""Construye anexos trazables a partir del código y evidencias reales."""
import ast
import json
from pathlib import Path
import subprocess

RAIZ = Path(__file__).resolve().parents[1]


def leer(ruta):
    return (RAIZ / ruta).read_text(encoding="utf-8-sig")


def escribir(ruta, texto):
    destino = RAIZ / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=RAIZ).decode("utf-8", errors="replace").strip()


def fragmento(ruta, nombre, limite=18):
    fuente = leer(ruta)
    nodo = next(n for n in ast.walk(ast.parse(fuente))
                if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == nombre)
    fin = min(nodo.end_lineno, nodo.lineno + limite - 1)
    lineas = fuente.splitlines()[nodo.lineno - 1:fin]
    return f"{ruta}, líneas {nodo.lineno}-{fin}.\n\n```python\n" + "\n".join(lineas) + "\n```\n"


def main():
    historial = git("log", "--reverse", "--format=%h | %s")
    escribir("evidencias/historial_desarrollo.txt", historial + "\n")
    inicial = leer("versiones/inicial/sistema.py")
    final = leer("sistema.py")
    metricas = []
    for etiqueta, fuente in (("Inicial", inicial), ("Final", final)):
        nodos = [n for n in ast.walk(ast.parse(fuente)) if isinstance(n, ast.FunctionDef)]
        operar = next(n for n in nodos if n.name == "operar")
        metricas.append((etiqueta, operar.end_lineno - operar.lineno + 1, len(nodos)))
    escribir("evidencias/metricas.json", json.dumps(metricas, indent=2))

    refactorings = """# Refactorings verificables

Las cuatro transformaciones se hicieron en commits reales, en el orden del historial. Las pruebas preceden a los cambios y se repiten por hito. Los fragmentos siguientes se extraen del código; cuando son parciales se indica su rango. No se alteraron los registros históricos para aparentar trabajo previo.

## R1 - Extract Method y validación compartida

CS01, CS02 y parte de CS07. Commit 32d2492. Se dividió el despachador en operaciones y se extrajo la validación repetida del nombre. SRP y legibilidad: cada caso de uso se inspecciona por separado. La interfaz operar y los errores permanecieron. Ver 02_extract_method.txt: 29 pruebas aprobadas.

"""
    refactorings += fragmento("versiones/inicial/sistema.py", "operar", 15)
    refactorings += fragmento("sistema.py", "operar")
    refactorings += fragmento("dominio.py", "validar_texto")
    refactorings += """
## R2 - Move Method / reubicación de persistencia

CS03 y CS08. Commit 1cfd75c: conexión, esquema y transacciones se movieron al repositorio. El registro 03_move_method.txt conserva 29 aprobadas. La revisión detectó que el servicio todavía contenía SQL; a379c39 completó el encapsulamiento con métodos semánticos. Esa diferencia se declara para no atribuir al primer paso una separación que todavía no tenía. SRP y DIP parcial.

"""
    refactorings += fragmento("versiones/inicial/sistema.py", "__init__", 17)
    refactorings += fragmento("repositorio.py", "agregar_solicitud")
    refactorings += fragmento("sistema.py", "__init__")
    refactorings += """
## R3 - Introduce Parameter Object

CS04. Commit b5eb55f. NuevaSolicitud reúne los seis datos de una solicitud; guardar_solicitud recibe ese objeto. La API posicional original se conserva como adaptador, por lo que la simplificación no exige romper clientes. No se presenta como eliminación total de la firma larga. Registro 04_parameter_object.txt: 29 aprobadas. La prueba adicional test_objeto_parametros comprueba la nueva vía.

"""
    refactorings += fragmento("versiones/inicial/sistema.py", "registrar_solicitud")
    refactorings += fragmento("dominio.py", "NuevaSolicitud")
    refactorings += fragmento("sistema.py", "guardar_solicitud", 18)
    refactorings += """
## R4 - Decompose Conditional y reglas separadas

CS05 y CS06; completa CS03, CS07 y CS08. Commit a379c39. La condición compuesta se reemplazó por una consulta a TRANSICIONES, con catálogos compartidos. La creación del repositorio también materializa Extract Class. Se preservan exactamente las cuatro transiciones permitidas. OCP localizado: cambia la tabla, no el algoritmo. Registro 05_separar_reglas.txt: 29 aprobadas; la revisión posterior recorre los 16 pares.

"""
    lineas = inicial.splitlines()
    comienzo = next(i for i, l in enumerate(lineas) if 'elif op == "estado"' in l)
    refactorings += f"versiones/inicial/sistema.py, líneas {comienzo+1}-{comienzo+11}.\n\n```python\n" + "\n".join(lineas[comienzo:comienzo+11]) + "\n```\n"
    refactorings += "dominio.py, tabla de transiciones.\n\n```python\n" + "\n".join(leer("dominio.py").splitlines()[5:12]) + "\n```\n"
    refactorings += fragmento("dominio.py", "validar_transicion")
    escribir("docs/refactorings.md", refactorings)

    casos = [
        ("Estudiante válido", "Demo; demo@example.test", "ID 1"),
        ("Email duplicado", "Mismo email con mayúsculas", "Email ya registrado"),
        ("Nombre vacío", "nombre vacío", "Nombre obligatorio"),
        ("Email inválido", "incorrecto", "Email inválido"),
        ("Solicitud válida", "Certificado, alta, estudiante 1", "Fila completa; pendiente"),
        ("Asunto vacío", "espacios", "Asunto obligatorio; no persiste"),
        ("Descripción vacía", "cadena vacía", "Descripción obligatoria; no persiste"),
        ("Tipo inválido", "otro", "Tipo inválido; no persiste"),
        ("Prioridad inválida", "urgente", "Prioridad inválida; no persiste"),
        ("Estudiante inexistente", "ID 999", "Estudiante inexistente"),
        ("Responsable inicial inexistente", "ID 999", "Responsable inexistente"),
        ("Asignar responsable", "Solicitud 1; responsable 1", "responsable_id=1"),
        ("Responsable al crear", "Responsable válido", "Asignación persistida"),
        ("Ciclo normal", "pendiente; en_proceso; resuelta", "Dos cambios válidos"),
        ("Salto inválido", "pendiente a resuelta", "Transición inválida; conserva estado"),
        ("Estado repetido", "pendiente a pendiente", "Transición inválida"),
        ("Estado desconocido", "desconocido", "Transición inválida"),
        ("Cancelación terminal", "cancelada a en_proceso", "Transición inválida"),
        ("Filtros y búsqueda", "alta, pendiente, CONSTANCIA y %", "Resultados combinados y búsqueda literal"),
        ("Filtro estado inválido", "otro", "Estado inválido"),
        ("Filtro prioridad inválida", "otra", "Prioridad inválida"),
        ("Reporte", "Base vacía y una pendiente", "Total 0 y 1; estados en cero incluidos"),
        ("Consulta inexistente", "ID 999", "Solicitud inexistente"),
        ("Cambio inexistente", "ID 999", "Solicitud inexistente"),
        ("Asignación inexistente", "ID 999", "Solicitud inexistente"),
        ("Responsable al asignar inexistente", "ID 999", "Rechazo; mantiene sin responsable"),
        ("Persistencia", "Cerrar y reabrir archivo", "Mismo asunto y solicitud"),
        ("SQL como dato", "Texto con DROP TABLE", "Se guarda literal; tabla conservada"),
        ("Operación desconocida", "borrar_todo", "Operación desconocida"),
    ]
    pruebas = "# Casos de prueba y resultados\n\n"
    pruebas += "Los identificadores P01-P29 organizan los casos por funcionalidad; unittest los imprime ordenados por nombre de método. Antes: registro 01_inicial.txt. Después: 05_separar_reglas.txt y 07_revision_optimizada.txt. En las columnas se indica coincidencia con el resultado esperado, no salidas fabricadas.\n\n"
    pruebas += "| ID | Caso y entrada | Resultado esperado | Antes | Después |\n|---|---|---|---|---|\n"
    for i, (nombre, entrada, esperado) in enumerate(casos, 1):
        pruebas += f"| P{i:02} | {nombre}: {entrada} | {esperado} | Coincide | Coincide |\n"
    pruebas += """
## Verificaciones añadidas en revisión

R01 recorre 16 pares de estados, con cuatro permitidos y doce rechazados. R02 prueba NuevaSolicitud. R03 inyecta un doble de conteos para reporte sin SQLite. R04 ejecuta una CLI con ID inexistente y verifica JSON, código 1 y ausencia de stderr. Estas cuatro pruebas no existían en la suite inicial; no se presentan como comparación antes/después.

La versión final ejecutó 33 pruebas. La matriz de 16 pares cuenta como un método con subcasos. demo.py realiza además diez pasos por versión y compara salida y código. No se midió cobertura; no se promete verificación exhaustiva.

## Método

Cada prueba de servicio abre SQLite en memoria y cierra la conexión. La persistencia se prueba con un archivo temporal reabierto. Las pruebas de consola usan procesos reales y bases temporales. No se usa una base de producción ni se limpian archivos del usuario. Los registros son salidas capturadas de los comandos ejecutados; no son capturas recreadas gráficamente.
"""
    escribir("docs/pruebas.md", pruebas)

    informe = """# 1. Resumen ejecutivo

Se construyó un prototipo local para gestionar solicitudes académicas.
La versión inicial resolvía los casos previstos, pero concentraba reglas y SQL.
El diagnóstico identificó ocho debilidades de legibilidad, cohesión y acoplamiento.
Se aplicaron cuatro refactorizaciones y se conservó la interfaz de consola.
Las 29 pruebas compartidas aprobaron por hito; la revisión final alcanzó 33.
Diez pasos de consola dieron resultados idénticos entre las dos versiones.

# 2. Introducción y objetivos

El trabajo se centra en mejorar un módulo acotado sin ampliar sus funciones por acumulación. Para ello se creó un prototipo expresamente para esta actividad. No se lo presenta como un sistema institucional anterior ni como una solución de producción. Su organización inicial, monolítica y simple, permite analizar dificultades reales de mantenimiento sin introducir fallos funcionales a propósito.

El objetivo general es mostrar una relación verificable entre diagnóstico, cambio y prueba. Los objetivos concretos son separar responsabilidades, reducir duplicaciones, simplificar datos de entrada y explicitar las reglas de estados. Cada mejora se vincula con una debilidad y con registros de ejecución reales.

Este documento está identificado a nombre de Gevont Utmazian, comisión M25 C4-08. La generación contó con asistencia sustancial de IA. La revisión personal, la justificación de modalidad individual, los enlaces externos y la defensa todavía requieren intervención del estudiante. No se atribuyen autorizaciones ni aprendizajes personales no comprobados.

# 3. Sistema base y alcance

El sistema representa el registro de solicitudes por parte de un operador de una institución educativa. El estudiante es el solicitante; el responsable representa a una persona o área que atiende el trámite. En este prototipo ninguno inicia sesión: el operador usa una consola local. No se confundieron actores del dominio con cuentas autenticadas.

| Estructura | Datos principales | Relación |
|---|---|---|
| Estudiante | id, nombre, email único | Uno a muchas solicitudes |
| Responsable | id, nombre | Cero o uno por solicitud |
| Solicitud | estudiante, tipo, prioridad, asunto, descripción, estado, responsable | Referencias protegidas por claves foráneas |
| Estado | pendiente, en_proceso, resuelta, cancelada | Valor del dominio; no tabla adicional |

Se implementan ocho operaciones de consola: registrar estudiante, registrar responsable, registrar solicitud, asignar, cambiar estado, consultar, listar con filtros y reportar. Tipos: certificado, equivalencia e inscripcion. Prioridades: baja, media y alta. Todas las solicitudes nuevas comienzan pendientes.

No se incluyen adjuntos, autenticación, eliminación, notificaciones, plazos ni uso simultáneo multiusuario. La prioridad clasifica, pero no ordena automáticamente una cola. El reporte cuenta solicitudes por estado. La búsqueda opera sobre el asunto y trata el texto de forma literal.

## 3.1 Tecnología y ejecución

Python permite resolver consola, pruebas y persistencia con su biblioteca estándar. SQLite usa un archivo local y no requiere servidor [R2]. unittest organiza fixtures y casos automatizados [R1]. Se usó Python 3.10.0 disponible en el equipo; no se instaló pytest porque el intento de descarga fue bloqueado por la red. Esta adaptación fue técnica, no un requisito de la cátedra.

```text
python -m unittest discover -s tests -v
python demo.py
python cli.py --db prueba.db reporte
```

La versión inicial se identifica con estado-inicial y se conserva también en versiones/inicial. El esquema de base no cambia, por lo que la comparación no necesita migraciones. Los datos usados en la demostración son ficticios.

# 4. Calidad externa, deuda técnica y diagnóstico

"""
    informe += leer("docs/diagnostico.md").replace("# Diagnóstico del estado inicial", "## 4.1 Diagnóstico documentado").replace("## Calidad externa e interna", "## 4.2 Comparación de calidad")
    informe += "\n## 4.3 Ubicaciones comprobables\n\n"
    patrones = [("CS01", "def operar"), ("CS02", 'd.get("nombre")'),
                ("CS03", "sqlite3.connect"), ("CS04", "def registrar_solicitud"),
                ("CS05", '("baja", "media", "alta")'), ("CS06", 'if not ((r["estado"]'),
                ("CS07", 'q = "SELECT'), ("CS08", 'SELECT id FROM estudiantes')]
    for ident, patron in patrones:
        indices = [i for i, l in enumerate(lineas) if patron in l]
        posicion = indices[0]
        informe += f"### {ident} - versiones/inicial/sistema.py:{posicion+1}\n\n```python\n" + "\n".join(lineas[posicion:posicion+3]) + "\n```\n\n"
    informe += "# 5. SOLID, Clean Code y decisiones\n\n" + leer("docs/principios_y_decisiones.md").replace("# Principios y decisiones", "")
    informe += "\n# 6. Refactoring seguro\n\n" + refactorings.replace("# Refactorings verificables", "")
    informe += "\n## 6.5 Indicadores estructurales\n\n| Versión | Líneas de operar | Funciones en sistema.py |\n|---|---|---|\n"
    for etiqueta, longitud, cantidad in metricas:
        informe += f"| {etiqueta} | {longitud} | {cantidad} |\n"
    informe += "\nSe contaron líneas físicas del nodo AST y funciones declaradas. El número total de funciones puede aumentar al extraer responsabilidades. Estos datos no prueban una mejora de rendimiento ni constituyen una métrica de calidad por sí solos.\n"
    informe += "\n# 7. Pruebas y verificación\n\n" + pruebas.replace("# Casos de prueba y resultados", "")
    informe += "\n## 7.1 Registros de ejecución\n\n"
    for ruta in sorted((RAIZ / "evidencias/pruebas").glob("*.txt")):
        contenido = ruta.read_text(encoding="utf-8-sig")
        resumen = "\n".join(contenido.splitlines()[-5:])
        informe += f"### {ruta.name}\n\nExtracto final del registro auténtico; archivo completo incluido en el anexo ZIP.\n\n```text\n{resumen}\n```\n"
    demo = json.loads(leer("evidencias/demo_comparada.json"))
    informe += "\n## 7.2 Demostración antes/después\n\nLa ejecución de demo.py informó IGUALES para diez pasos. Ejemplos de resultados realmente capturados:\n\n"
    for indice in (2, 7, 8, 9):
        paso = demo["final"][indice]
        informe += "```json\n" + json.dumps(paso, ensure_ascii=False, indent=2) + "\n```\n"
    informe += "\n# 8. Code review y criterios de aceptación\n\n" + leer("docs/checklist_code_review.md").replace("# Autorrevisión técnica asistida por IA", "## Autorrevisión técnica asistida por IA")
    informe += """
# 9. Conclusiones y mejoras futuras

El resultado más relevante es la separación entre reglas de aplicación y acceso a datos. Antes, el mismo método contenía validaciones, consultas y cambios de estado. Después, el servicio expresa las operaciones y el repositorio administra las consultas. La tabla de transiciones permite inspeccionar el ciclo sin reconstruir una expresión booleana extensa.

El proceso también mostró que una extracción superficial puede no resolver el problema completo. Mover únicamente la conexión dejó SQL dentro del servicio; fue necesario encapsular las consultas para completar esa mejora. La revisión de pruebas detectó otra debilidad: las aserciones nativas podían omitirse con optimización. Se sustituyeron y se verificó la suite con python -O.

No se afirma que el sistema esté libre de errores. La evidencia respalda el contrato cubierto. Quedan pendientes mensajes para errores técnicos, validación de email más estricta, búsqueda Unicode completa, autenticación y concurrencia. Esos cambios deberían planificarse como mejoras funcionales separadas y con pruebas propias.

## Conclusión individual propuesta para Gevont Utmazian

Borrador para revisar tras estudiar y ejecutar el proyecto: «La comparación muestra que un programa puede dar resultados correctos y aun así ser difícil de mantener. Separar las reglas y el almacenamiento ayuda a ubicar los cambios, y las pruebas permiten comprobar que esa reorganización conserva el comportamiento esperado. El criterio principal no fue sumar funciones, sino poder justificar las mejoras con ejemplos y resultados.»

Este párrafo no certifica un aprendizaje personal ya demostrado. El estudiante debe reemplazarlo o ampliarlo con su reflexión real. No se incluye una conclusión grupal ficticia porque el material está preparado para modalidad individual todavía por confirmar.

# 10. Uso de inteligencia artificial

"""
    informe += leer("docs/registro_ia.md").replace("# Registro de intervención de IA", "")
    informe += """
# 11. Referencias y recursos

[R1] Python Software Foundation. Documentación de unittest, Python 3.10. Consulta: 01/11/2026. https://docs.python.org/3.10/library/unittest.html

[R2] Python Software Foundation. Documentación de sqlite3, Python 3.10. Consulta: 01/11/2026. https://docs.python.org/3.10/library/sqlite3.html

[R3] Martin Fowler. Refactoring Catalog: Extract Function (alias Extract Method). Consulta: 01/11/2026. https://refactoring.com/catalog/extractFunction.html

[R4] Martin Fowler. Refactoring Catalog: Introduce Parameter Object. Consulta: 01/11/2026. https://refactoring.com/catalog/introduceParameterObject.html

Los términos Extract Method e Introduce Parameter Object se emplean según esas entradas del catálogo [R3, R4]. Los fragmentos del informe son del proyecto, no copias de los ejemplos del sitio.

[C1] Cátedra de Metodología de Sistemas II. TP MS2V2.pdf, seis páginas, suministrado por el usuario. Fuente principal de requisitos.

[C2] Material complementario suministrado como Markdown pegado(1).md. Incluye orientaciones de entrega y defensa. Se conserva como docs/material_catedra.md.

Repositorio GitHub: PENDIENTE DE PUBLICACIÓN AUTORIZADA.

Video personal: PENDIENTE DE GRABACIÓN Y ENLACE.

Fecha de entrega y justificación individual: PENDIENTES DE CONFIRMACIÓN.

# 12. Auditoría y cierre de entrega

"""
    informe += leer("docs/auditoria.md") if (RAIZ / "docs/auditoria.md").exists() else "Ver docs/matriz_requisitos.md; auditoría final en preparación.\n"
    informe += "\n# Anexo A. Historial real de desarrollo\n\nEste extracto cubre el desarrollo y la verificación. Los commits posteriores de documentación y los tags finales se consultan en historial.bundle. No se inventan fechas anteriores.\n\n```text\n" + historial + "\n```\n"
    informe += "\n# Anexo B. Prompt maestro suministrado\n\nSe conserva el texto completo extraído, normalizando únicamente saltos de línea. Es una instrucción del usuario, no una afirmación de que todas sus propuestas tecnológicas fueran requisitos de la cátedra. Los pendientes de entrega se declaran en la auditoría.\n\n"
    # Lower heading levels in the quoted prompt to keep the main TOC usable.
    prompt = leer("docs/prompt_maestro.txt")
    informe += "\n".join("### " + l.lstrip("# ") if l.startswith("#") else l for l in prompt.splitlines())
    escribir("informe/Informe_TPI_MS2_Gevont_Utmazian.md", informe + "\n")


if __name__ == "__main__":
    main()
