# Diagnóstico del estado inicial

La referencia estable es `estado-inicial:sistema.py`. El prototipo fue construido para el TPI con una organización monolítica deliberadamente simple. No se presenta como software heredado de una institución. Funciona en los 29 casos de contrato ejecutados, pero modificarlo exige conocer SQL, reglas de negocio y el despachador de operaciones en una misma clase.

| ID | Debilidad y ubicación | Evidencia literal | Impacto y riesgo | Prioridad | Corrección prevista |
|---|---|---|---|---|---|
| CS01 | Long Method: `Sistema.operar` | `def operar(self, op, **d)` contiene todas las ramas | Una edición puede afectar operaciones no relacionadas; cuesta revisar el flujo completo | Alta | R1 Extract Method |
| CS02 | Duplicación: ramas estudiante/responsable | `if not isinstance(d.get("nombre"), str) or not d["nombre"].strip()` | Dos validaciones iguales pueden divergir | Media | R1 función de texto obligatorio |
| CS03 | Clase con responsabilidades mezcladas: `Sistema` | `sqlite3.connect(ruta)` y `raise ValueError("Transición inválida")` | Persistencia y política de estados cambian por razones diferentes | Alta | R2 Move Method, R4 Extract Class |
| CS04 | Long Parameter List: `registrar_solicitud` | `estudiante_id, tipo, prioridad, asunto, descripcion, responsable_id=None` | Es fácil intercambiar cadenas posicionales del mismo tipo | Media | R3 Introduce Parameter Object |
| CS05 | Literales de dominio repetidos: solicitud/listar | `("baja", "media", "alta")` | Un valor nuevo requiere cambios en puntos separados | Media | R4 constantes compartidas |
| CS06 | Condicional compuesto: cambio de estado | `(r["estado"] == "pendiente" and ...) or (...)` | Al ampliar el ciclo es fácil habilitar una transición incorrecta | Alta | R4 tabla de transiciones |
| CS07 | Nombres abreviados: listado y conexión | `q`, `p`, `r`, `d`, `self.c` | La lectura depende de reconstruir el significado local | Baja | R1 nombres de parámetros y R2 repositorio |
| CS08 | Acoplamiento a la base de datos: creación y consultas | `self.c.execute(...)` dentro de reglas de negocio | Probar una política exige montar SQLite; cambiar persistencia afecta el servicio | Alta | R2 acceso encapsulado y R4 inyección de repositorio |

CS03 describe la falta de cohesión de la clase; CS08, la dependencia concreta de sus reglas. Están relacionados, pero sus consecuencias y verificaciones son diferentes. Ninguno implica que el programa sea inseguro por definición: las consultas ya usan parámetros y las claves foráneas están activadas.

La prioridad alta se reserva para cambios que afectan reglas o varias operaciones. La media corresponde a duplicaciones y firmas que multiplican el costo del cambio. La baja corresponde a legibilidad localizada. No se asignaron tiempos ni costos económicos ficticios.

## Calidad externa e interna

| Situación | Observación externa | Observación interna |
|---|---|---|
| Registrar una solicitud válida | Devuelve un identificador y conserva los datos | Una rama combina consultas previas, validaciones y SQL de inserción |
| Rechazar datos incompletos | Mensaje específico y ninguna solicitud persistida | La validación de texto se repite |
| Cambiar estado | Impide saltar de pendiente a resuelta | Las reglas están embebidas en una expresión booleana |
| Filtrar y reportar | Devuelve filas ordenadas y totales consistentes | Literales y acceso a datos viven en el mismo despachador |

Las pruebas externas caracterizan el comportamiento, no certifican por sí solas mantenibilidad, rendimiento o seguridad integral. Los 29 casos iniciales se ejecutaron con `python -m unittest discover -s tests -v`; el registro auténtico está en `evidencias/pruebas/01_inicial.txt`.
