"""Muestra resultados reales para documentarlos con una captura de la consola."""
import argparse
import json

from demo import RAIZ, ejecutar


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=("inicial", "final"))
    version = parser.parse_args().version
    carpeta = RAIZ / "versiones" / "inicial" if version == "inicial" else RAIZ
    pasos = ejecutar(carpeta)
    print(f"Solicitudes académicas | versión {version} | datos de ejemplo")
    for indice, titulo in ((2, "Alta de solicitud"), (7, "Consulta después del cambio"),
                           (8, "Transición rechazada"), (9, "Reporte")):
        paso = pasos[indice]
        print(f"\n{titulo} | código de salida: {paso['codigo']}")
        print(json.dumps(paso["salida"], ensure_ascii=False))


if __name__ == "__main__":
    main()
