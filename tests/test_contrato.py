"""Contrato observable: la misma suite se ejecuta antes y después."""
import pytest
from sistema import Sistema


@pytest.fixture
def sistema():
    servicio = Sistema()
    yield servicio
    servicio.cerrar()


def solicitud(sistema, **cambios):
    estudiante = sistema.operar("estudiante", nombre="Estudiante Demo", email="demo@example.test")
    datos = dict(estudiante_id=estudiante, tipo="certificado", prioridad="alta",
                 asunto="Constancia regular", descripcion="Para beca ficticia")
    datos.update(cambios)
    return sistema.operar("solicitud", **datos)


def test_estudiante_valido(sistema):
    assert sistema.operar("estudiante", nombre=" Demo ", email="DEMO@example.test") == 1


def test_email_duplicado(sistema):
    sistema.operar("estudiante", nombre="Uno", email="demo@example.test")
    with pytest.raises(ValueError, match="Email ya registrado"):
        sistema.operar("estudiante", nombre="Dos", email="DEMO@example.test")


@pytest.mark.parametrize("datos,mensaje", [
    ({"nombre": "", "email": "a@b"}, "Nombre obligatorio"),
    ({"nombre": "Demo", "email": "incorrecto"}, "Email inválido")])
def test_estudiante_invalido(sistema, datos, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        sistema.operar("estudiante", **datos)


def test_solicitud_valida(sistema):
    identificador = solicitud(sistema)
    fila = sistema.operar("consultar", id=identificador)
    assert fila == dict(id=1, estudiante_id=1, tipo="certificado", prioridad="alta",
                        asunto="Constancia regular", descripcion="Para beca ficticia",
                        estado="pendiente", responsable_id=None)


@pytest.mark.parametrize("cambio,mensaje", [
    ({"asunto": " "}, "Asunto obligatorio"),
    ({"descripcion": ""}, "Descripción obligatoria"),
    ({"tipo": "otro"}, "Tipo inválido"),
    ({"prioridad": "urgente"}, "Prioridad inválida"),
    ({"estudiante_id": 999}, "Estudiante inexistente"),
    ({"responsable_id": 999}, "Responsable inexistente")])
def test_solicitud_invalida_no_persiste(sistema, cambio, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        solicitud(sistema, **cambio)
    assert sistema.operar("listar") == []


def test_asignar_responsable(sistema):
    identificador = solicitud(sistema)
    responsable = sistema.operar("responsable", nombre="Área Demo")
    assert sistema.operar("asignar", id=identificador, responsable_id=responsable) is None
    assert sistema.operar("consultar", id=identificador)["responsable_id"] == responsable


def test_responsable_al_crear(sistema):
    responsable = sistema.operar("responsable", nombre="Área Demo")
    identificador = solicitud(sistema, responsable_id=responsable)
    assert sistema.operar("consultar", id=identificador)["responsable_id"] == responsable


def test_ciclo_de_estados(sistema):
    identificador = solicitud(sistema)
    for estado in ("en_proceso", "resuelta"):
        sistema.operar("estado", id=identificador, estado=estado)
        assert sistema.operar("consultar", id=identificador)["estado"] == estado


@pytest.mark.parametrize("estado", ["resuelta", "pendiente", "desconocido"])
def test_transicion_invalida(sistema, estado):
    identificador = solicitud(sistema)
    with pytest.raises(ValueError, match="Transición inválida"):
        sistema.operar("estado", id=identificador, estado=estado)
    assert sistema.operar("consultar", id=identificador)["estado"] == "pendiente"


def test_cancelacion_terminal(sistema):
    identificador = solicitud(sistema)
    sistema.operar("estado", id=identificador, estado="cancelada")
    with pytest.raises(ValueError, match="Transición inválida"):
        sistema.operar("estado", id=identificador, estado="en_proceso")


def test_filtros_y_busqueda(sistema):
    solicitud(sistema)
    sistema.registrar_solicitud(1, "inscripcion", "baja", "Otra gestión", "Detalle")
    assert len(sistema.operar("listar")) == 2
    assert len(sistema.operar("listar", prioridad="alta", estado="pendiente", texto="CONSTANCIA")) == 1
    assert sistema.operar("listar", estado="resuelta") == []
    assert sistema.operar("listar", texto="%") == []


@pytest.mark.parametrize("datos,mensaje", [({"estado": "otro"}, "Estado inválido"),
                                         ({"prioridad": "otra"}, "Prioridad inválida")])
def test_filtro_invalido(sistema, datos, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        sistema.operar("listar", **datos)


def test_reporte(sistema):
    assert sistema.operar("reporte")["total"] == 0
    solicitud(sistema)
    assert sistema.operar("reporte") == {"total": 1, "por_estado": {
        "pendiente": 1, "en_proceso": 0, "resuelta": 0, "cancelada": 0}}


@pytest.mark.parametrize("operacion,datos", [
    ("consultar", {"id": 999}), ("estado", {"id": 999, "estado": "en_proceso"}),
    ("asignar", {"id": 999, "responsable_id": 1})])
def test_solicitud_inexistente(sistema, operacion, datos):
    with pytest.raises(ValueError, match="Solicitud inexistente"):
        sistema.operar(operacion, **datos)


def test_responsable_inexistente(sistema):
    identificador = solicitud(sistema)
    with pytest.raises(ValueError, match="Responsable inexistente"):
        sistema.operar("asignar", id=identificador, responsable_id=999)
    assert sistema.operar("consultar", id=identificador)["responsable_id"] is None


def test_persistencia(tmp_path):
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


def test_entrada_sql_se_trata_como_texto(sistema):
    texto = "'; DROP TABLE estudiantes; --"
    solicitud(sistema, asunto=texto)
    assert sistema.operar("consultar", id=1)["asunto"] == texto
    assert sistema.operar("estudiante", nombre="Otra", email="otra@example.test") == 2


def test_operacion_desconocida(sistema):
    with pytest.raises(ValueError, match="Operación desconocida"):
        sistema.operar("borrar_todo")
