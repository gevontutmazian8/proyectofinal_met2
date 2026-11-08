# Autorrevisión técnica asistida por IA

Revisión del artefacto por el mismo asistente que lo generó, el 01/11/2026. No constituye revisión independiente ni aprobación de un compañero o docente. Con dos integrantes corresponde registrar antes de entregar una revisión cruzada real (cada uno revisa el aporte del otro en el repositorio); hasta entonces consta sólo la autorrevisión asistida.

| Criterio | Resultado | Evidencia o límite |
|---|---|---|
| Legibilidad y nombres | Conforme con límite | Métodos descriptivos; API compatible conserva diccionarios |
| Responsabilidades y cohesión | Conforme | Consola, servicio, dominio y repositorio separados |
| Duplicación | Conforme con límite | Validación de texto común; catálogo centralizado. Literal pendiente sigue en SQL de inserción |
| Complejidad | Conforme al alcance | Operaciones separadas; estados definidos por tabla |
| Validaciones | Conforme al contrato | Rechazos no crean solicitudes; mensajes conservados |
| Manejo de errores | Parcial | Errores de dominio controlados; fallos de disco/SQLite no traducidos en la CLI |
| Acoplamiento y SOLID | Parcial justificado | Inyección disponible; dependencia predeterminada SQLite permanece |
| Persistencia | Conforme | Reapertura probada, claves foráneas y transacciones |
| Seguridad básica | Conforme al alcance | SQL parametrizado, datos sintéticos; sin autenticación |
| Pruebas | Conforme | 29 casos de contrato y 4 revisiones; matriz de 16 pares de estados |
| Organización | Conforme | Versión inicial conservada; evidencias separadas |
| Documentación | Conforme al contenido local | README, diagnóstico, refactorings, IA, defensa e informe |
| Mantenibilidad | Mejorada con deuda residual | No se atribuye escalabilidad ni preparación para producción |
| Entrega externa | Pendiente | GitHub, video y confirmación administrativa |

## Observaciones y acciones

| ID | Archivo | Severidad | Observación y recomendación | Acción y estado |
|---|---|---|---|---|
| CR01 | sistema.py, hito Move Method | Media | Mover sólo conexión dejaba SQL en las reglas. Encapsular también consultas | Corregido en a379c39: métodos semánticos del repositorio |
| CR02 | tests/test_contrato.py | Media | Suite de contrato no recorre todos los pares de estados | Se añadió test_matriz_completa_transiciones: 16 subcasos, sin cambiar producción |
| CR03 | cli.py | Media | Las pruebas del servicio no garantizan salida de consola | demo.py compara diez pasos reales; prueba adicional verifica error y código 1 |
| CR04 | sistema.py | Baja | Inyección sin prueba de sustitución | Se agregó doble mínimo para reporte; no se lo presenta como repositorio completo |
| CR05 | dominio.py, repositorio.py | Baja | Estado inicial pendiente también aparece como literal SQL | Deuda residual aceptada; no se inventa eliminación total de literales |
| CR06 | cli.py | Media | Error de disco/base dañada puede generar traceback | Pendiente de mejora funcional independiente; documentado en README |
| CR07 | tests/test_contrato.py | Media | Asserts nativos pueden omitirse con python -O | Reemplazados por aserciones unittest y ejecutada la suite con optimización |

## Criterios de aceptación técnica

La suite compartida debe aprobar en el estado inicial y en cada refactoring. La demostración debe devolver igualdad exacta. No debe existir SQL en el servicio final. El ZIP debe poder extraerse y ejecutar pruebas sin instalar paquetes. Deben existir los seis tags y un historial recuperable. Los pendientes externos deben permanecer visibles en el informe.

El resultado local no se presenta como una entrega académica completa mientras falten enlaces y video personal.
