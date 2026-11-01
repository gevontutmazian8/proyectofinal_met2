# Casos de prueba y resultados

Los identificadores P01-P29 organizan los casos por funcionalidad; unittest los imprime ordenados por nombre de método. Antes: registro 01_inicial.txt. Después: 05_separar_reglas.txt y 07_revision_optimizada.txt. En las columnas se indica coincidencia con el resultado esperado, no salidas fabricadas.

| ID | Caso y entrada | Resultado esperado | Antes | Después |
|---|---|---|---|---|
| P01 | Estudiante válido: Demo; demo@example.test | ID 1 | Coincide | Coincide |
| P02 | Email duplicado: Mismo email con mayúsculas | Email ya registrado | Coincide | Coincide |
| P03 | Nombre vacío: nombre vacío | Nombre obligatorio | Coincide | Coincide |
| P04 | Email inválido: incorrecto | Email inválido | Coincide | Coincide |
| P05 | Solicitud válida: Certificado, alta, estudiante 1 | Fila completa; pendiente | Coincide | Coincide |
| P06 | Asunto vacío: espacios | Asunto obligatorio; no persiste | Coincide | Coincide |
| P07 | Descripción vacía: cadena vacía | Descripción obligatoria; no persiste | Coincide | Coincide |
| P08 | Tipo inválido: otro | Tipo inválido; no persiste | Coincide | Coincide |
| P09 | Prioridad inválida: urgente | Prioridad inválida; no persiste | Coincide | Coincide |
| P10 | Estudiante inexistente: ID 999 | Estudiante inexistente | Coincide | Coincide |
| P11 | Responsable inicial inexistente: ID 999 | Responsable inexistente | Coincide | Coincide |
| P12 | Asignar responsable: Solicitud 1; responsable 1 | responsable_id=1 | Coincide | Coincide |
| P13 | Responsable al crear: Responsable válido | Asignación persistida | Coincide | Coincide |
| P14 | Ciclo normal: pendiente; en_proceso; resuelta | Dos cambios válidos | Coincide | Coincide |
| P15 | Salto inválido: pendiente a resuelta | Transición inválida; conserva estado | Coincide | Coincide |
| P16 | Estado repetido: pendiente a pendiente | Transición inválida | Coincide | Coincide |
| P17 | Estado desconocido: desconocido | Transición inválida | Coincide | Coincide |
| P18 | Cancelación terminal: cancelada a en_proceso | Transición inválida | Coincide | Coincide |
| P19 | Filtros y búsqueda: alta, pendiente, CONSTANCIA y % | Resultados combinados y búsqueda literal | Coincide | Coincide |
| P20 | Filtro estado inválido: otro | Estado inválido | Coincide | Coincide |
| P21 | Filtro prioridad inválida: otra | Prioridad inválida | Coincide | Coincide |
| P22 | Reporte: Base vacía y una pendiente | Total 0 y 1; estados en cero incluidos | Coincide | Coincide |
| P23 | Consulta inexistente: ID 999 | Solicitud inexistente | Coincide | Coincide |
| P24 | Cambio inexistente: ID 999 | Solicitud inexistente | Coincide | Coincide |
| P25 | Asignación inexistente: ID 999 | Solicitud inexistente | Coincide | Coincide |
| P26 | Responsable al asignar inexistente: ID 999 | Rechazo; mantiene sin responsable | Coincide | Coincide |
| P27 | Persistencia: Cerrar y reabrir archivo | Mismo asunto y solicitud | Coincide | Coincide |
| P28 | SQL como dato: Texto con DROP TABLE | Se guarda literal; tabla conservada | Coincide | Coincide |
| P29 | Operación desconocida: borrar_todo | Operación desconocida | Coincide | Coincide |

## Verificaciones añadidas en revisión

R01 recorre 16 pares de estados, con cuatro permitidos y doce rechazados. R02 prueba NuevaSolicitud. R03 inyecta un doble de conteos para reporte sin SQLite. R04 ejecuta una CLI con ID inexistente y verifica JSON, código 1 y ausencia de stderr. Estas cuatro pruebas no existían en la suite inicial; no se presentan como comparación antes/después.

La versión final ejecutó 33 pruebas. La matriz de 16 pares cuenta como un método con subcasos. demo.py realiza además diez pasos por versión y compara salida y código. No se midió cobertura; no se promete verificación exhaustiva.

## Método

Cada prueba de servicio abre SQLite en memoria y cierra la conexión. La persistencia se prueba con un archivo temporal reabierto. Las pruebas de consola usan procesos reales y bases temporales. No se usa una base de producción ni se limpian archivos del usuario. Los registros son salidas capturadas de los comandos ejecutados; no son capturas recreadas gráficamente.
