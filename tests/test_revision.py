"""Comprobaciones añadidas durante la revisión final."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dominio import NuevaSolicitud, validar_transicion
from sistema import Sistema


class Revision(unittest.TestCase):
    def test_matriz_completa_transiciones(self):
        estados = ("pendiente", "en_proceso", "resuelta", "cancelada")
        permitidas = {("pendiente", "en_proceso"), ("pendiente", "cancelada"),
                      ("en_proceso", "resuelta"), ("en_proceso", "cancelada")}
        for actual in estados:
            for destino in estados:
                with self.subTest(actual=actual, destino=destino):
                    if (actual, destino) in permitidas:
                        self.assertIsNone(validar_transicion(actual, destino))
                    else:
                        with self.assertRaisesRegex(ValueError, "Transición inválida"):
                            validar_transicion(actual, destino)

    def test_objeto_parametros(self):
        sistema = Sistema()
        try:
            estudiante = sistema.operar("estudiante", nombre="Demo", email="demo@example.test")
            nueva = NuevaSolicitud(estudiante_id=estudiante, tipo="certificado", prioridad="media",
                                   asunto="Constancia", descripcion="Detalle")
            self.assertEqual(sistema.guardar_solicitud(nueva), 1)
        finally:
            sistema.cerrar()

    def test_servicio_usa_repositorio_sustituto_para_reporte(self):
        class ConteosEnMemoria:
            def contar_por_estado(self):
                return {"pendiente": 2, "resuelta": 1}
        sistema = Sistema(repositorio=ConteosEnMemoria())
        self.assertEqual(sistema.operar("reporte"), {"total": 3, "por_estado": {
            "pendiente": 2, "en_proceso": 0, "resuelta": 1, "cancelada": 0}})

    def test_cli_error_controlado(self):
        raiz = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as carpeta:
            proceso = subprocess.run([sys.executable, str(raiz / "cli.py"), "--db",
                str(Path(carpeta) / "cli.db"), "consultar", "--id", "999"],
                capture_output=True, text=True, encoding="utf-8",
                env={**__import__('os').environ, 'PYTHONUTF8': '1'})
        self.assertEqual(proceso.returncode, 1)
        self.assertEqual(json.loads(proceso.stdout), {"ok": False, "error": "Solicitud inexistente"})
        self.assertEqual(proceso.stderr, "")
