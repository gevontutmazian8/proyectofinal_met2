# Pasos que requieren al estudiante

1. Confirmar con la cátedra la modalidad individual. El PDF admite entrega individual con justificación; el complemento menciona justificación/autorización. No se inventa un motivo personal ni una autorización. Registrar la justificación real y la respuesta de la cátedra.
2. Confirmar la fecha de entrega en la plataforma. La fecha de elaboración es 01/11/2026 y no equivale al vencimiento.
3. Revisar el código y ejecutar README. Estudiar el guion y las preguntas, especialmente límites y uso de IA.
4. Autorizar la publicación y elegir cuenta/organización y nombre de repositorio. El repositorio local ya está preparado. Tras crear un remoto vacío, agregar su URL real, subir rama y tags. No usar push --force. No hay un remoto creado por el asistente.
5. Grabar 10 a 15 minutos con rostro, nombre y voz propios. El guion es una ayuda, no un video terminado.
6. Incorporar las URL reales de GitHub y del video en la fuente del informe, regenerar el PDF y actualizar el ZIP. Probar acceso a ambos enlaces sin depender de la sesión del propietario.
7. Cargar PDF, repositorio, ZIP y video. Sólo entonces puede considerarse completa la entrega de recursos.

Comandos orientativos después de autorizar y crear el repositorio vacío, sustituyendo URL_REAL por el dato comprobado:

```powershell
git remote add origin URL_REAL
git push -u origin master
git push origin --tags
```

No ejecutar el ejemplo con URL_REAL literal. Si ya existe un remoto, inspeccionarlo antes de modificarlo. El archivo historial.bundle permite recuperar el repositorio sin conexión.
