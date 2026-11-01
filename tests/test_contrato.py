"""Contrato ejecutable sin dependencias externas: unittest."""

import unittest
import tempfile
from pathlib import Path
from sistema import Sistema


def solicitud(sistema, **cambios):
    estudiante = sistema.operar("estudiante", nombre="Estudiante Demo", email="demo@example.test")
    datos = dict(estudiante_id=estudiante, tipo="certificado", prioridad="alta",
                 asunto="Constancia regular", descripcion="Para beca ficticia")
    datos.update(cambios)
    return sistema.operar("solicitud", **datos)

class Contrato(unittest.TestCase):
    def setUp(self):
        self.sistema = Sistema()
        self.temporal = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.sistema.cerrar()
        self.temporal.cleanup()


    def test_estudiante_valido(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        assert sistema.operar("estudiante", nombre=" Demo ", email="DEMO@example.test") == 1

    def test_email_duplicado(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        sistema.operar("estudiante", nombre="Uno", email="demo@example.test")
        with self.assertRaisesRegex(ValueError, "Email ya registrado"):
            sistema.operar("estudiante", nombre="Dos", email="DEMO@example.test")

    def test_estudiante_invalido_01(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        datos = {'nombre': '', 'email': 'a@b'}

        mensaje = 'Nombre obligatorio'

        with self.assertRaisesRegex(ValueError, mensaje):
            sistema.operar("estudiante", **datos)

    def test_estudiante_invalido_02(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        datos = {'nombre': 'Demo', 'email': 'incorrecto'}

        mensaje = 'Email inválido'

        with self.assertRaisesRegex(ValueError, mensaje):
            sistema.operar("estudiante", **datos)

    def test_solicitud_valida(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        identificador = solicitud(sistema)
        fila = sistema.operar("consultar", id=identificador)
        assert fila == dict(id=1, estudiante_id=1, tipo="certificado", prioridad="alta",
                            asunto="Constancia regular", descripcion="Para beca ficticia",
                            estado="pendiente", responsable_id=None)

    def test_solicitud_invalida_no_persiste_01(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        cambio = {'asunto': ' '}

        mensaje = 'Asunto obligatorio'

        with self.assertRaisesRegex(ValueError, mensaje):
            solicitud(sistema, **cambio)
        assert sistema.operar("listar") == []

    def test_solicitud_invalida_no_persiste_02(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        cambio = {'descripcion': ''}

        mensaje = 'Descripción obligatoria'

        with self.assertRaisesRegex(ValueError, mensaje):
            solicitud(sistema, **cambio)
        assert sistema.operar("listar") == []

    def test_solicitud_invalida_no_persiste_03(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        cambio = {'tipo': 'otro'}

        mensaje = 'Tipo inválido'

        with self.assertRaisesRegex(ValueError, mensaje):
            solicitud(sistema, **cambio)
        assert sistema.operar("listar") == []

    def test_solicitud_invalida_no_persiste_04(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        cambio = {'prioridad': 'urgente'}

        mensaje = 'Prioridad inválida'

        with self.assertRaisesRegex(ValueError, mensaje):
            solicitud(sistema, **cambio)
        assert sistema.operar("listar") == []

    def test_solicitud_invalida_no_persiste_05(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        cambio = {'estudiante_id': 999}

        mensaje = 'Estudiante inexistente'

        with self.assertRaisesRegex(ValueError, mensaje):
            solicitud(sistema, **cambio)
        assert sistema.operar("listar") == []

    def test_solicitud_invalida_no_persiste_06(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        cambio = {'responsable_id': 999}

        mensaje = 'Responsable inexistente'

        with self.assertRaisesRegex(ValueError, mensaje):
            solicitud(sistema, **cambio)
        assert sistema.operar("listar") == []

    def test_asignar_responsable(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        identificador = solicitud(sistema)
        responsable = sistema.operar("responsable", nombre="Área Demo")
        assert sistema.operar("asignar", id=identificador, responsable_id=responsable) is None
        assert sistema.operar("consultar", id=identificador)["responsable_id"] == responsable

    def test_responsable_al_crear(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        responsable = sistema.operar("responsable", nombre="Área Demo")
        identificador = solicitud(sistema, responsable_id=responsable)
        assert sistema.operar("consultar", id=identificador)["responsable_id"] == responsable

    def test_ciclo_de_estados(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        identificador = solicitud(sistema)
        for estado in ("en_proceso", "resuelta"):
            sistema.operar("estado", id=identificador, estado=estado)
            assert sistema.operar("consultar", id=identificador)["estado"] == estado

    def test_transicion_invalida_01(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        estado = 'resuelta'

        identificador = solicitud(sistema)
        with self.assertRaisesRegex(ValueError, "Transición inválida"):
            sistema.operar("estado", id=identificador, estado=estado)
        assert sistema.operar("consultar", id=identificador)["estado"] == "pendiente"

    def test_transicion_invalida_02(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        estado = 'pendiente'

        identificador = solicitud(sistema)
        with self.assertRaisesRegex(ValueError, "Transición inválida"):
            sistema.operar("estado", id=identificador, estado=estado)
        assert sistema.operar("consultar", id=identificador)["estado"] == "pendiente"

    def test_transicion_invalida_03(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        estado = 'desconocido'

        identificador = solicitud(sistema)
        with self.assertRaisesRegex(ValueError, "Transición inválida"):
            sistema.operar("estado", id=identificador, estado=estado)
        assert sistema.operar("consultar", id=identificador)["estado"] == "pendiente"

    def test_cancelacion_terminal(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        identificador = solicitud(sistema)
        sistema.operar("estado", id=identificador, estado="cancelada")
        with self.assertRaisesRegex(ValueError, "Transición inválida"):
            sistema.operar("estado", id=identificador, estado="en_proceso")

    def test_filtros_y_busqueda(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        solicitud(sistema)
        sistema.registrar_solicitud(1, "inscripcion", "baja", "Otra gestión", "Detalle")
        assert len(sistema.operar("listar")) == 2
        assert len(sistema.operar("listar", prioridad="alta", estado="pendiente", texto="CONSTANCIA")) == 1
        assert sistema.operar("listar", estado="resuelta") == []
        assert sistema.operar("listar", texto="%") == []

    def test_filtro_invalido_01(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        datos = {'estado': 'otro'}

        mensaje = 'Estado inválido'

        with self.assertRaisesRegex(ValueError, mensaje):
            sistema.operar("listar", **datos)

    def test_filtro_invalido_02(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        datos = {'prioridad': 'otra'}

        mensaje = 'Prioridad inválida'

        with self.assertRaisesRegex(ValueError, mensaje):
            sistema.operar("listar", **datos)

    def test_reporte(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        assert sistema.operar("reporte")["total"] == 0
        solicitud(sistema)
        assert sistema.operar("reporte") == {"total": 1, "por_estado": {
            "pendiente": 1, "en_proceso": 0, "resuelta": 0, "cancelada": 0}}

    def test_solicitud_inexistente_01(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        operacion = 'consultar'

        datos = {'id': 999}

        with self.assertRaisesRegex(ValueError, "Solicitud inexistente"):
            sistema.operar(operacion, **datos)

    def test_solicitud_inexistente_02(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        operacion = 'estado'

        datos = {'id': 999, 'estado': 'en_proceso'}

        with self.assertRaisesRegex(ValueError, "Solicitud inexistente"):
            sistema.operar(operacion, **datos)

    def test_solicitud_inexistente_03(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        operacion = 'asignar'

        datos = {'id': 999, 'responsable_id': 1}

        with self.assertRaisesRegex(ValueError, "Solicitud inexistente"):
            sistema.operar(operacion, **datos)

    def test_responsable_inexistente(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        identificador = solicitud(sistema)
        with self.assertRaisesRegex(ValueError, "Responsable inexistente"):
            sistema.operar("asignar", id=identificador, responsable_id=999)
        assert sistema.operar("consultar", id=identificador)["responsable_id"] is None

    def test_persistencia(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        ruta = str(tmp_path / "prueba.db")
        primero = Sistema(ruta)
        try:
            solicitud(primero)
        finally:
            primero.cerrar()
        segundo = Sistema(ruta)
        try:
            assert segundo.operar("consultar", id=1)["asunto"] == "Constancia regular"
        finally:
            segundo.cerrar()

    def test_entrada_sql_se_trata_como_texto(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        texto = "'; DROP TABLE estudiantes; --"
        solicitud(sistema, asunto=texto)
        assert sistema.operar("consultar", id=1)["asunto"] == texto
        assert sistema.operar("estudiante", nombre="Otra", email="otra@example.test") == 2

    def test_operacion_desconocida(self):

        sistema = self.sistema
        tmp_path = Path(self.temporal.name)

        with self.assertRaisesRegex(ValueError, "Operación desconocida"):
            sistema.operar("borrar_todo")

if __name__ == '__main__':
    unittest.main(verbosity=2)
