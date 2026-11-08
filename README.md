# Sistema de Gestión de Solicitudes Académicas

TPI de Metodología de Sistemas II. Integrantes: Gevont Utmazian y Martín Maine. Comisión M25 C4-08, 2026.

Prototipo académico creado expresamente para analizar calidad interna, diagnosticar ocho debilidades y refactorizar sin cambiar el contrato externo. La generación de código, pruebas y documentación contó con intervención sustancial de ChatGPT/Codex; ver `docs/registro_ia.md`. La comprensión y defensa de los integrantes están pendientes de realizarse.

## Ejecutar desde cero

Descomprimir el ZIP y abrir una terminal dentro de esta carpeta. Se requiere Python 3.10 o superior; fue probado con 3.10.0 en Windows. Para una instalación nueva usar una versión mantenida de Python compatible; no se necesita instalar paquetes para ejecutar el sistema ni las pruebas. SQLite, argparse, dataclasses y unittest están incluidos en Python.

```powershell
python --version
python -m unittest discover -s tests -v
python demo.py
```

La demostración crea bases temporales, ejecuta diez pasos en cada versión y compara exactamente JSON y códigos de salida. No modifica una base de trabajo existente.

## Capturas para el informe

Desde la carpeta del proyecto, ejecutá cada comando por separado:

```powershell
python -m herramientas.capturas inicial
python -m herramientas.capturas final
python -m unittest discover -s tests
```

Después de cada ejecución, usá **Win + Mayús + S** para capturar el comando y su salida. Guardá las imágenes como `01_inicial.png`, `02_final.png` y `03_pruebas.png` en `evidencias/capturas/`. Las primeras dos ejecuciones usan la misma demostración y datos ficticios sobre bases temporales.

## Uso de la consola

Los siguientes comandos suponen un archivo `mi_prueba.db` nuevo. Si ya tiene datos, usar los identificadores devueltos en lugar de asumir que son 1. Todas las operaciones usan el mismo archivo indicado con `--db`.

```powershell
python cli.py --db mi_prueba.db estudiante --nombre "Estudiante Demo" --email "demo@example.test"
python cli.py --db mi_prueba.db responsable --nombre "Secretaría Demo"
python cli.py --db mi_prueba.db solicitud --estudiante-id 1 --tipo certificado --prioridad alta --asunto "Constancia regular" --descripcion "Beca ficticia"
python cli.py --db mi_prueba.db asignar --id 1 --responsable-id 1
python cli.py --db mi_prueba.db estado --id 1 --estado en_proceso
python cli.py --db mi_prueba.db listar --prioridad alta --estado en_proceso --texto Constancia
python cli.py --db mi_prueba.db estado --id 1 --estado resuelta
python cli.py --db mi_prueba.db consultar --id 1
python cli.py --db mi_prueba.db reporte
```

Tipos: certificado, equivalencia, inscripcion. Prioridades: baja, media, alta. Una solicitud empieza pendiente; puede pasar a en_proceso o cancelada. Desde en_proceso puede pasar a resuelta o cancelada. Los dos últimos estados son terminales. No se exige responsable para avanzar: esa regla no existía en la versión inicial.

Los errores de validación producen JSON con `ok: false` y código de salida 1. El éxito devuelve `ok: true` y código 0. Los errores de argumentos los informa argparse. Una ruta sin permisos o una base dañada puede producir un error técnico: es una limitación documentada, no una validación de negocio.

## Organización

| Archivo/carpeta | Función |
|---|---|
| cli.py | Argumentos y salida JSON |
| sistema.py | Servicio y adaptadores compatibles |
| dominio.py | NuevaSolicitud, constantes y transiciones |
| repositorio.py | Esquema, SQL y transacciones |
| versiones/inicial | Copia exacta del código base |
| tests | 29 casos compartidos y 4 verificaciones de revisión |
| docs | Diagnóstico, decisiones, revisión, IA y auditoría |
| evidencias | Registros auténticos de pruebas y demostración |
| informe | PDF y fuente Markdown editable |
| presentacion | Presentación del TPI (PPTX y PDF) sobre el modelo de la cátedra |
| defensa | Guion y preguntas para estudiar |

La persistencia tiene tres tablas: estudiantes, responsables y solicitudes. Estado es un conjunto de valores del dominio, no una cuarta tabla. No hay autenticación, adjuntos, borrado ni concurrencia multiusuario. La búsqueda ignora mayúsculas ASCII; SQLite no garantiza equivalencia Unicode completa en `lower`. La validación de email es básica y se conserva para evitar cambios funcionales durante el refactoring.

## Historial y estados

| Tag | Referencia |
|---|---|
| estado-inicial | Prototipo con 29 pruebas ejecutadas |
| etapa-diagnostico | Ocho debilidades y copia de referencia |
| etapa-refactoring | Cuatro transformaciones estructurales verificadas |
| etapa-pruebas | Comparación de consolas y suite ampliada |
| etapa-docs | Informe y documentación |
| estadorefactorizado | Estado final auditado |

El ZIP contiene `historial.bundle`, que conserva todos los commits y tags sin depender de un enlace remoto. Para recuperar el repositorio completo, desde una carpeta distinta:

```powershell
git clone historial.bundle TPI_con_historial
git -C TPI_con_historial log --oneline --decorate
git -C TPI_con_historial tag --list
```

El registro de intervención de IA está en `docs/registro_ia.md`. La participación de cada integrante figura en la sección 2.1 del informe.

## Informe editable

El PDF y la fuente están en `informe/`. Para regenerarlo se necesita ReportLab, solamente para documentación:

```powershell
python -m pip install reportlab
python herramientas/generar_informe.py
```

La sección 12 del informe contiene el enlace del repositorio y el campo del video de defensa.
