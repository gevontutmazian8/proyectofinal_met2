# Guion de defensa - Gevont Utmazian

Duración objetivo: 10 a 15 minutos. Ensayar con cronómetro: el tiempo depende de la demostración y de las pausas. Usar rostro y voz propios. Este guion es un borrador; no afirmar que se entiende algo que todavía no se puede explicar. El trabajo fue generado con asistencia sustancial de IA y eso debe declararse.

## 0:00 a 1:00 - Presentación

Mostrar cámara y portada.

«Hola, soy Gevont Utmazian, de la comisión M25 C4-08. En este trabajo de Metodología de Sistemas II analizo un sistema pequeño de solicitudes académicas. La idea es comparar una versión que funciona, pero está organizada de una manera difícil de mantener, con una versión que conserva ese funcionamiento y separa mejor las responsabilidades.

El prototipo se construyó para esta actividad. Utilicé ChatGPT/Codex con una intervención importante en el código, las pruebas y la documentación; eso está registrado en el informe. Esta defensa sirve para explicar y justificar las decisiones del proyecto.»

Antes de usar esa presentación, estudiar los archivos y realizar personalmente la demostración. No agregar afirmaciones de trabajo manual propio que no hayan ocurrido.

## 1:00 a 2:30 - Qué hace el sistema

Abrir README y una terminal dentro del proyecto. Ejecutar los comandos de alta de estudiante, responsable y solicitud sobre una base nueva. Mostrar los identificadores devueltos.

«El sistema sirve para registrar pedidos como certificados, equivalencias o inscripciones. Una solicitud pertenece a un estudiante, tiene tipo, prioridad y estado, y puede tener un responsable. Los datos se guardan en SQLite, en un archivo local.

La aplicación tiene una consola. No se hizo una web porque el objetivo del trabajo es analizar y mejorar el código, y una interfaz más grande habría agregado tareas que no eran necesarias. El uso es local y no hay autenticación ni trabajo simultáneo de varios operadores.»

Mostrar asignación y cambio a en_proceso. Explicar que pendiente no pasa directamente a resuelta.

## 2:30 a 4:30 - Diagnóstico

Abrir versiones/inicial/sistema.py y docs/diagnostico.md.

«La calidad externa es lo que se puede observar al usar el programa: que registre los datos, devuelva resultados correctos y rechace una transición inválida. La calidad interna tiene que ver con cómo está escrito: si se puede leer, probar y modificar sin afectar otras partes.

En la versión inicial, operar reúne prácticamente todos los casos de uso. Además, la misma clase abre SQLite, valida los datos y hace las consultas. Eso no impide que funcione, pero hace más costoso un cambio.

Se documentaron ocho debilidades. Entre ellas están el método extenso, la repetición de validaciones, la lista larga de parámetros, los nombres abreviados y el condicional de estados. No todas tienen la misma prioridad: separar reglas de almacenamiento es más importante que cambiar un nombre local.»

Señalar dos fragmentos reales y leer su impacto. No limitarse a recitar los ocho nombres.

## 4:30 a 7:30 - Refactorizaciones

Abrir sistema.py, dominio.py y repositorio.py. Mostrar git log --oneline.

«El primer cambio fue Extract Method. Se separaron las ramas del método grande en operaciones más pequeñas y se extrajo la validación repetida del nombre. El segundo fue mover la responsabilidad de persistencia a un repositorio. Al principio se había movido sólo la conexión; la revisión mostró que eso no alcanzaba y también se encapsularon las consultas.

El tercer cambio fue Introduce Parameter Object. NuevaSolicitud agrupa los datos que antes viajaban en seis argumentos. La firma antigua se mantiene como adaptador para no romper llamadas existentes. El código nuevo puede pasar un objeto con campos nombrados.

El cuarto cambio separó las reglas y reemplazó la expresión de transiciones por una tabla. Ahora se puede ver qué estados son posibles sin leer un condicional largo. El comportamiento se mantuvo: resuelta y cancelada son terminales.»

Mostrar TRANSICIONES y explicar dos ejemplos, uno permitido y uno rechazado.

«SRP se ve en la separación de responsabilidades. DIP se aplica parcialmente porque puedo pasar un repositorio al servicio, aunque SQLite sigue como opción predeterminada. OCP mejora en la tabla de estados. No agregamos herencia para aparentar una aplicación de LSP, ni interfaces grandes sólo para mencionar ISP.»

## 7:30 a 9:30 - Pruebas

Ejecutar `python -m unittest discover -s tests -v`. Luego `python demo.py`; mostrar comparacion: IGUALES y un paso de error.

«La versión inicial pasó 29 casos. Esos mismos casos se repitieron después de cada refactoring. Incluyen altas, datos inválidos, filtros, persistencia y errores por identificadores inexistentes.

En la revisión se agregaron cuatro pruebas. Una recorre las 16 combinaciones entre estados; esos subcasos están dentro de una prueba y no se suman como si fueran 16 métodos distintos. El resultado final es 33 pruebas aprobadas.

También se compararon diez pasos de la consola en ambas versiones. Se comparan el JSON y el código de salida, no sólo que el programa termine. Esto da evidencia de ausencia de regresiones en los casos cubiertos; no demuestra que sea imposible encontrar un error.»

Explicar por qué las pruebas usan bases temporales y no modifican datos de trabajo.

## 9:30 a 11:30 - Revisión

Abrir docs/checklist_code_review.md y evidencias/pruebas/07_revision_optimizada.txt.

«La revisión es una autorrevisión asistida por IA, no una revisión externa. El checklist contempla responsabilidades, duplicación, pruebas, persistencia y errores. Una corrección fue reemplazar asserts nativos por aserciones de unittest: los asserts pueden omitirse con Python optimizado, y las pruebas no deberían perder sus comprobaciones.

También quedaron límites documentados. La validación de email es básica, los errores técnicos de disco no tienen un mensaje amigable y la aplicación no resuelve concurrencia multiusuario. No se corrigieron silenciosamente durante el refactoring porque cambiarían el alcance o el comportamiento.»

## 11:30 a 13:00 - Cierre

Mostrar comparación de estructura e informe.

«La mejora principal está en que las reglas y el almacenamiento ya no están mezclados. El sistema no tiene muchas más funciones, pero cada cambio se puede ubicar mejor. El historial y los registros permiten comprobar cómo se llegó a esa versión.

El punto central del trabajo es que funcionar correctamente y estar bien organizado son cosas relacionadas, pero distintas. La refactorización busca mejorar la organización sin perder lo que ya funcionaba. Las pruebas permiten controlar ese proceso dentro de los casos que se definieron.»

Agregar una reflexión personal sólo después de estudiar y ejecutar el trabajo: qué parte costó comprender, qué decisión se reconsideraría y qué se pudo verificar personalmente.
