# Principios y decisiones

## SOLID aplicado con límites explícitos

| Principio | Problema y cambio | Alcance real |
|---|---|---|
| SRP | Sistema mezclaba SQL y reglas. RepositorioSQLite administra almacenamiento; dominio concentra reglas; cli presenta resultados | Aplicado directamente. El servicio coordina casos de uso |
| OCP | El ciclo de estados estaba escrito como expresión booleana. TRANSICIONES permite cambiar relaciones sin editar el algoritmo de validación | Mejora localizada: una operación nueva todavía exige modificar el despachador. No se afirma cumplimiento absoluto |
| LSP | No hay jerarquía de herencia de producción que requiera sustitución de subclases | No se fuerza. La prueba de un repositorio mínimo demuestra sustitución solamente para reporte, no equivalencia total de repositorios |
| ISP | No se agregó una interfaz universal con operaciones ajenas al caso de uso | No se introducen interfaces nominales. El reporte utiliza únicamente contar_por_estado; una división mayor sería innecesaria para este alcance |
| DIP | El constructor acepta un repositorio; las reglas ya no ejecutan SQL | Aplicación parcial mediante inyección y contrato estructural. Sistema todavía importa SQLite como opción predeterminada; un composition root independiente sería una mejora futura |

Clean Code se aplica mediante nombres descriptivos, validación reutilizable, métodos acotados y mensajes estables. Se mantiene una firma antigua con seis parámetros como adaptador: retirarla rompería compatibilidad. El código nuevo puede usar guardar_solicitud(NuevaSolicitud(...)) con nombres explícitos.

## Decisiones técnicas

1. Python y SQLite permiten ejecutar el sistema sin servidor ni servicios externos. Las tres tablas y sus relaciones cubren el alcance sin un ORM.
2. unittest reemplazó la propuesta inicial pytest: pytest no estaba instalado y la instalación falló por restricciones de red. Se conservaron los mismos casos e intenciones. No se declara una ejecución de pytest.
3. Python 3.10.0 fue el intérprete disponible y efectivamente usado. La propuesta 3.11 no era un requisito obligatorio. No se recomienda instalar una versión antigua para producción.
4. Las transacciones cubren cada escritura. No se implementó un flujo transaccional multiusuario entre lectura y actualización: la aplicación es local, de un operador.
5. Se mantienen validación básica de email, búsqueda SQL y reglas iniciales. Corregirlas ahora sería un cambio funcional que debe separarse de la refactorización.
6. No se eliminó la API operar ni se alteró el esquema de SQLite. Las salidas JSON de diez pasos fueron idénticas entre ambas consolas.
7. Los datos de ejemplo son sintéticos. El nombre académico sólo aparece en documentación y no se incorpora como dato de estudiante del sistema.
8. No se calcularon cobertura ni métricas de complejidad ciclomática con herramientas externas. Las métricas estructurales del anexo se obtienen con ast y no son una puntuación de calidad.

## Relaciones y componentes

Un estudiante puede tener varias solicitudes. Una solicitud tiene exactamente un estudiante y cero o un responsable. Un responsable puede atender varias solicitudes. La prioridad y el tipo clasifican; el estado representa el avance. La consola llama al servicio; éste utiliza reglas de dominio y el repositorio; únicamente el repositorio conoce SQL.
