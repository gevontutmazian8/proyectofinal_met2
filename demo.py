"""Demostración reproducible: compara las dos consolas sobre bases temporales."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

RAIZ = Path(__file__).resolve().parent
PASOS = [
    ["estudiante", "--nombre", "Estudiante Demo", "--email", "demo@example.test"],
    ["responsable", "--nombre", "Secretaría Demo"],
    ["solicitud", "--estudiante-id", "1", "--tipo", "certificado", "--prioridad", "alta",
     "--asunto", "Constancia regular", "--descripcion", "Beca ficticia"],
    ["asignar", "--id", "1", "--responsable-id", "1"],
    ["estado", "--id", "1", "--estado", "en_proceso"],
    ["listar", "--prioridad", "alta"],
    ["estado", "--id", "1", "--estado", "resuelta"],
    ["consultar", "--id", "1"],
    ["estado", "--id", "1", "--estado", "pendiente"],
    ["reporte"],
]


def ejecutar(carpeta):
    salidas = []
    with tempfile.TemporaryDirectory(prefix="tpi_demo_") as temporal:
        for paso in PASOS:
            resultado = subprocess.run([sys.executable, str(carpeta / "cli.py"), "--db",
                str(Path(temporal) / "demo.db"), *paso], capture_output=True, text=True,
                encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
            if resultado.stderr:
                raise RuntimeError(resultado.stderr)
            contenido = json.loads(resultado.stdout)
            esperado = 0 if contenido["ok"] else 1
            if resultado.returncode != esperado:
                raise RuntimeError("Código de salida incoherente")
            salidas.append({"argumentos": paso, "salida": contenido, "codigo": resultado.returncode})
    return salidas


if __name__ == "__main__":
    inicial = ejecutar(RAIZ / "versiones" / "inicial")
    final = ejecutar(RAIZ)
    if inicial != final:
        raise SystemExit("DIFERENCIA: revisar resultados")
    print(json.dumps({"comparacion": "IGUALES", "pasos": len(final),
                      "inicial": inicial, "final": final}, ensure_ascii=False, indent=2))
