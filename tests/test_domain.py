import pytest
from decimal import Decimal
from app.domain import Money, InvalidOrderData, InvalidOrderTransition, OrderStatus
from cargar_csv import load_fixture


# Prueba 1: Validar el Value Object Money
def test_money_negativo():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-1"))


# Prueba 2: Validar el estado inicial y totales del pedido O001
def test_pedido_o001_inicia_draft():
    orders = load_fixture()
    order = orders["O001"]

    assert order.status == OrderStatus.DRAFT
    assert order.units == 4
    assert order.total.amount == Decimal("2100.00")


# Prueba 3: Validar que un pedido vacío lanza error 422 (InvalidOrderData)
def test_confirmar_pedido_vacio_falla():
    orders = load_fixture()
    order = orders["O007"]  # El pedido O007 no tiene artículos en los datos

    with pytest.raises(InvalidOrderData, match="Requiere artículos"):
        order.confirm()


# Prueba 4: Validar que la transición de estado protege la lógica (Error 409)
def test_confirmacion_doble_falla():
    orders = load_fixture()
    order = orders["O013"]

    order.confirm()  # Primera confirmación exitosa

    with pytest.raises(InvalidOrderTransition, match="Solo se puede confirmar un pedido DRAFT"):
        order.confirm()  # Segunda confirmación debe fallar


# Prueba 5: Validar límite máximo de unidades
def test_limite_de_20_unidades():
    orders = load_fixture()
    order = orders["O008"]  # Este ya tiene 20 artículos
    from app.domain import OrderItem, Money

    nuevo_item = OrderItem(sku="TEST", quantity=1, unit_price=Money(Decimal("100")))

    from app.domain import OrderItemLimitExceeded
    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(nuevo_item)