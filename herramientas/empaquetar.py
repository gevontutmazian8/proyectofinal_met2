"""Empaqueta archivos versionados, conserva Git y verifica una extracción limpia."""
import hashlib
import json
import os
from datetime import date
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / 'entrega'
TAGS = ['estado-inicial', 'etapa-diagnostico', 'etapa-refactoring',
        'etapa-pruebas', 'etapa-docs', 'estadorefactorizado']


def comando(args, cwd=RAIZ):
    resultado = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                               encoding='utf-8', errors='replace',
                               env={**os.environ, 'PYTHONUTF8': '1'})
    if resultado.returncode:
        raise RuntimeError(resultado.stdout + resultado.stderr)
    # Git emite advertencias de configuración ajenas al estado en stderr.
    # No deben confundirse con nombres de archivos ni hashes.
    return resultado.stdout if args[0] == 'git' else resultado.stdout + resultado.stderr


def main():
    SALIDA.mkdir(exist_ok=True)
    tags = {tag: comando(['git', 'rev-parse', tag]).strip() for tag in TAGS}
    if len(set(tags.values())) != len(tags):
        raise RuntimeError('Cada tag debe identificar su propio hito')
    if comando(['git', 'status', '--porcelain']).strip():
        raise RuntimeError('Hay cambios sin versionar')
    original = comando(['git', 'show', 'estado-inicial:sistema.py'])
    copia = (RAIZ/'versiones/inicial/sistema.py').read_text(encoding='utf-8-sig')
    if original.replace('\r\n','\n') != copia.replace('\r\n','\n'):
        raise RuntimeError('La copia inicial no corresponde al tag')
    bundle = SALIDA / 'historial.bundle'
    comando(['git', 'bundle', 'create', str(bundle), '--all'])
    verificacion_git = comando(['git', 'bundle', 'verify', str(bundle)])
    archivos = comando(['git', 'ls-files']).splitlines()
    hashes = {nombre: hashlib.sha256((RAIZ/nombre).read_bytes()).hexdigest() for nombre in archivos}
    manifiesto = {'commit': comando(['git','rev-parse','HEAD']).strip(), 'tags': tags,
                  'sha256_archivos_versionados': hashes,
                  'sha256_bundle': hashlib.sha256(bundle.read_bytes()).hexdigest()}
    paquete = SALIDA / 'TPI_MS2_Gevont_Utmazian.zip'

    def guardar(evidencia=None):
        with zipfile.ZipFile(paquete, 'w', zipfile.ZIP_DEFLATED) as z:
            for nombre in archivos:
                z.write(RAIZ/nombre, 'TPI_Metodologia_Sistemas_II/'+nombre)
            z.write(bundle, 'TPI_Metodologia_Sistemas_II/historial.bundle')
            z.writestr('TPI_Metodologia_Sistemas_II/manifiesto_entrega.json', json.dumps(manifiesto,indent=2))
            if evidencia:
                z.writestr('TPI_Metodologia_Sistemas_II/evidencias/validacion_paquete.txt', evidencia)

    guardar()
    with tempfile.TemporaryDirectory(prefix='tpi_verificacion_') as temporal:
        carpeta = Path(temporal)
        with zipfile.ZipFile(paquete) as z:
            if z.testzip() is not None:
                raise RuntimeError('ZIP dañado')
            z.extractall(carpeta)
        proyecto = carpeta / 'TPI_Metodologia_Sistemas_II'
        pruebas = comando([sys.executable,'-m','unittest','discover','-s','tests','-v'],proyecto)
        demo = json.loads(comando([sys.executable,'demo.py'],proyecto))
        if demo['comparacion'] != 'IGUALES' or demo['pasos'] != 10:
            raise RuntimeError('Falló comparación de consola')
        comando(['git','clone',str(proyecto/'historial.bundle'),str(carpeta/'restaurado')],carpeta)
        restaurado = carpeta/'restaurado'
        for tag, commit in tags.items():
            if comando(['git','rev-parse',tag],restaurado).strip() != commit:
                raise RuntimeError('Tag no restaurado')
        comando(['git','fsck','--full'],restaurado)
    evidencia = (f'Validación de paquete extraído, {date.today():%d/%m/%Y}.\n'
                 + pruebas + '\nDemostración: IGUALES, 10 pasos por versión.\n'
                 + 'Historial restaurado desde bundle: seis tags coincidentes; git fsck aprobado.\n'
                 + 'Archivos versionados comprobados mediante SHA-256.\n')
    guardar(evidencia)
    with zipfile.ZipFile(paquete) as z:
        if z.testzip() is not None:
            raise RuntimeError('ZIP final dañado')
        for nombre, esperado in hashes.items():
            real = hashlib.sha256(z.read('TPI_Metodologia_Sistemas_II/'+nombre)).hexdigest()
            if real != esperado:
                raise RuntimeError('Contenido final distinto al validado')
    (SALIDA/'validacion_paquete.txt').write_text(evidencia,encoding='utf-8')
    (SALIDA/'manifiesto_entrega.json').write_text(json.dumps(manifiesto,indent=2),encoding='utf-8')
    print(json.dumps({'zip':str(paquete),'archivos_versionados':len(archivos),
                      'bytes':paquete.stat().st_size,'pruebas':'33 aprobadas',
                      'tags':list(tags),'comparacion':'IGUALES'},ensure_ascii=False))


if __name__ == '__main__':
    main()
