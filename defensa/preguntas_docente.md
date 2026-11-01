# Preguntas para estudiar

## ¿Por qué refactorizar si el programa ya funcionaba?
Porque funcionar no asegura que sea fácil cambiarlo. Antes, modificar estados o almacenamiento exigía revisar un mismo método grande. Después hay lugares específicos para esas responsabilidades.

## ¿Qué diferencia hay entre un bug y un code smell?
Un bug produce un comportamiento incorrecto. Un smell es una señal de diseño que merece revisión, aunque el resultado sea correcto. Una función extensa puede pasar todas las pruebas y seguir siendo difícil de mantener.

## ¿Qué es deuda técnica en este caso?
Es el trabajo de mejora que se posterga y que puede encarecer cambios futuros. Por ejemplo, repetir prioridades en dos ramas permite que un cambio se aplique sólo en una. No se asignó un costo monetario inventado.

## ¿Qué cambió externamente?
La consola conserva operaciones, mensajes, JSON y esquema de base. Se añadió una vía interna con NuevaSolicitud y archivos de demostración/pruebas. No se incorporó una nueva regla de negocio como exigir responsable antes de avanzar.

## ¿Cómo explicás cada refactoring con un archivo?
Extract Method: operar y métodos pequeños en sistema.py. Move Method: conexión y consultas en repositorio.py. Introduce Parameter Object: NuevaSolicitud y guardar_solicitud. Decompose Conditional: validar_transicion y TRANSICIONES en dominio.py. La extracción del repositorio también corresponde a Extract Class.

## ¿Los seis parámetros desaparecieron completamente?
No. La firma vieja queda como adaptador de compatibilidad. La operación principal nueva recibe NuevaSolicitud. El beneficio es para llamadas nuevas sin romper las anteriores.

## ¿Se aplicaron los cinco principios SOLID?
Se analizaron los cinco. SRP se aplica directamente; OCP y DIP de forma localizada/parcial. No se necesita una jerarquía para LSP ni interfaces nominales para ISP. Sería incorrecto decir que todos están implementados por completo.

## ¿Qué prueba que no hay regresiones?
29 casos compartidos aprobados por hito y diez pasos equivalentes de consola. Es evidencia para ese contrato, no una prueba matemática de ausencia de errores. La suite final tiene 33 métodos de prueba.

## ¿Por qué unittest y no pytest?
pytest estaba propuesto, pero no estaba instalado y su instalación no pudo conectarse a la red. unittest ya estaba disponible y permite ejecutar el contrato sin dependencias. No se simuló una salida de pytest.

## ¿Qué pasa si se corta la ejecución durante una escritura?
Las escrituras usan el contexto de transacción de sqlite3. Ese contexto confirma si termina bien y revierte ante excepción. No significa que toda una secuencia de comandos de consola sea una única transacción.

## ¿Qué seguridad tiene?
Las consultas usan parámetros y las claves foráneas están activadas. Eso no reemplaza autenticación, autorización, backups ni controles de producción. El prototipo se limita a un operador local y datos ficticios.

## ¿Por qué existe una prueba con texto SQL?
Para comprobar que ese texto se trata como un dato y no como una instrucción. No es una auditoría de seguridad completa.

## ¿La tabla de estados resuelve OCP por completo?
No. Permite cambiar relaciones sin reescribir el algoritmo de transición. Agregar operaciones o modificar otras reglas todavía requiere código y pruebas.

## ¿Quién hizo la revisión y el desarrollo?
El asistente ChatGPT/Codex generó gran parte del material y ejecutó verificaciones. Está declarado. No hubo un compañero revisor. El estudiante debe describir honestamente qué estudió, verificó o modificó personalmente después.

## ¿Cuál es la principal limitación pendiente?
La entrega externa requiere repositorio publicado y video personal. En el software: validación básica, consola poco amigable, falta de autenticación y control multiusuario. Priorizaría mejorar mensajes de errores técnicos en un cambio funcional separado.

## Ejercicios antes de grabar

1. Crear una solicitud de prioridad baja y encontrarla con un filtro.
2. Intentar pasar directamente de pendiente a resuelta y explicar el rechazo.
3. Cerrar y abrir el programa y comprobar persistencia.
4. Señalar un fragmento antes/después sin leer el informe.
5. Explicar por qué una prueba aprobada no garantiza calidad interna.
6. Mostrar estado-inicial con git show sin modificar la carpeta de trabajo.
