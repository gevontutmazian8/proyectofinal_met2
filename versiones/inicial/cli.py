"""Interfaz de consola compartida por las versiones inicial y final."""
import argparse
import json
from sistema import Sistema


def main():
    parser = argparse.ArgumentParser(description="Gestión de solicitudes académicas")
    parser.add_argument("--db", default="solicitudes.db", help="Archivo SQLite")
    parser.add_argument("operacion", choices=["estudiante", "responsable", "solicitud", "asignar", "estado", "consultar", "listar", "reporte"])
    for campo in ("nombre", "email", "tipo", "prioridad", "asunto", "descripcion", "estado", "texto"):
        parser.add_argument("--" + campo)
    for campo in ("id", "estudiante_id", "responsable_id"):
        parser.add_argument("--" + campo.replace("_", "-"), type=int)
    args = vars(parser.parse_args())
    ruta, operacion = args.pop("db"), args.pop("operacion")
    sistema = Sistema(ruta)
    try:
        resultado = sistema.operar(operacion, **{k: v for k, v in args.items() if v is not None})
        print(json.dumps({"ok": True, "resultado": resultado}, ensure_ascii=False, indent=2))
    except ValueError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1
    finally:
        sistema.cerrar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
