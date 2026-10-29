"""Pruebas de los escenarios E01-E15 (datos de datos/escenarios.csv) y de reglas de borde.

Esquema de cada prueba: preparar datos (load_fixture), ejecutar la accion y comprobar el resultado.
"""
import csv
from decimal import Decimal
from pathlib import Path

import pytest

from app.domain import (
    Customer, InvalidOrderData, InvalidOrderTransition, Money, Order,
    OrderItem, OrderItemLimitExceeded, OrderStatus,
)
from app.specifications import discount_rate, five_percent, ten_percent
from cargar_csv import load_fixture


def nombres_eventos(order):
    return [e.name for e in order.events]


def pedido_vip(unidades, precio_unitario, promocion=False, vip=True):
    order = Order(customer=Customer("CX", vip, True), id="TX", has_promotion=promocion)
    order.add_item(OrderItem("SKU-T", unidades, Money(Decimal(precio_unitario))))
    return order


# ---------------------------------------------------------------- E01 a E05
def test_e01_o001_descuento_10():
    order = load_fixture()["O001"]
    assert discount_rate(order) == Decimal("0.10")
    assert ten_percent.is_satisfied_by(order)
    assert order.events == []


def test_e02_o002_sin_descuento_no_vip_menor_a_5000():
    order = load_fixture()["O002"]
    assert discount_rate(order) == Decimal("0")


def test_e03_o003_confirmar_cliente_inactivo_se_rechaza():
    order = load_fixture()["O003"]
    with pytest.raises(InvalidOrderData):
        order.confirm()
    assert order.status == OrderStatus.DRAFT
    assert order.events == []


def test_e04_o005_promocion_activa_bloquea_descuentos():
    order = load_fixture()["O005"]
    assert order.has_promotion
    assert discount_rate(order) == Decimal("0")


def test_e05_o006_descuento_5_por_total_mayor_a_5000():
    order = load_fixture()["O006"]
    assert order.total.amount == Decimal("18000.00")
    assert discount_rate(order) == Decimal("0.05")
    assert five_percent.is_satisfied_by(order)
    assert not ten_percent.is_satisfied_by(order)


# ---------------------------------------------------------------- E06 a E10
def test_e06_o007_confirmar_pedido_vacio_se_rechaza():
    order = load_fixture()["O007"]
    assert order.units == 0
    with pytest.raises(InvalidOrderData, match="Requiere artículos"):
        order.confirm()
    assert order.status == OrderStatus.DRAFT
    assert order.events == []


def test_e07_o008_veinte_unidades_se_pueden_confirmar():
    order = load_fixture()["O008"]
    assert order.units == 20
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert nombres_eventos(order) == ["OrderConfirmed"]


def test_e08_o009_agregar_supera_20_unidades_se_rechaza_sin_modificar_items():
    order = load_fixture()["O009"]
    renglones_antes = len(order.items)
    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(OrderItem("SKU003", 2, Money(Decimal("100"))))
    assert order.units == 19
    assert len(order.items) == renglones_antes
    assert order.events == []


def test_e09_o010_total_exacto_500_no_supera_el_umbral_estricto():
    order = load_fixture()["O010"]
    assert order.total.amount == Decimal("500.00")
    assert discount_rate(order) == Decimal("0")


def test_e10_o011_vip_con_3_unidades_no_alcanza_el_minimo_de_4():
    order = load_fixture()["O011"]
    assert order.customer.is_vip and order.units == 3
    assert discount_rate(order) == Decimal("0")


# --------------------------------------------------------------- E11 a E15
def test_e11_o012_enviar_sin_guia_se_rechaza_y_queda_confirmed():
    order = load_fixture()["O012"]
    order.confirm()
    with pytest.raises(InvalidOrderData, match="guía"):
        order.ship("")
    assert order.status == OrderStatus.CONFIRMED
    assert nombres_eventos(order) == ["OrderConfirmed"]


def test_e12_o013_segunda_confirmacion_se_rechaza_sin_nuevo_evento():
    order = load_fixture()["O013"]
    order.confirm()
    with pytest.raises(InvalidOrderTransition, match="DRAFT"):
        order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert nombres_eventos(order) == ["OrderConfirmed"]


def test_e13_o014_cancelar_desde_shipped_se_rechaza():
    order = load_fixture()["O014"]
    order.confirm()
    order.ship("GUIA-014")
    with pytest.raises(InvalidOrderTransition, match="CONFIRMED"):
        order.cancel("Ya no lo quiero")
    assert order.status == OrderStatus.SHIPPED
    assert nombres_eventos(order) == ["OrderConfirmed", "OrderShipped"]


def test_e14_o015_devolucion_desde_shipped_termina_en_returned():
    order = load_fixture()["O015"]
    order.confirm()
    order.ship("GUIA-015")
    order.return_order()
    assert order.status == OrderStatus.RETURNED
    assert nombres_eventos(order) == ["OrderConfirmed", "OrderShipped", "OrderReturned"]


def test_e15_o016_entrega_desde_shipped_termina_en_delivered():
    order = load_fixture()["O016"]
    order.confirm()
    order.ship("GUIA-016")
    order.deliver()
    assert order.status == OrderStatus.DELIVERED
    assert nombres_eventos(order) == ["OrderConfirmed", "OrderShipped", "OrderDelivered"]


# --------------------------------------------------- Coherencia con escenarios.csv
def test_los_15_escenarios_existen_y_apuntan_a_pedidos_cargados():
    ruta = Path(__file__).resolve().parent.parent / "datos" / "escenarios.csv"
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    pedidos = load_fixture()
    assert [f["caso_id"] for f in filas] == [f"E{i:02d}" for i in range(1, 16)]
    assert all(f["pedido_id"] in pedidos for f in filas)


def test_descuentos_calculados_coinciden_con_el_objetivo_del_csv():
    ruta = Path(__file__).resolve().parent.parent / "datos" / "escenarios.csv"
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        filas = [r for r in csv.DictReader(f) if r["accion"] == "evaluar_descuento"]
    pedidos = load_fixture()
    assert len(filas) == 6
    for fila in filas:
        calculado = f"{int(discount_rate(pedidos[fila['pedido_id']]) * 100)}%"
        assert calculado == fila["objetivo"], fila["caso_id"]


def test_todos_los_pedidos_cargados_inician_en_draft():
    pedidos = load_fixture()
    assert len(pedidos) == 16
    assert all(o.status == OrderStatus.DRAFT for o in pedidos.values())


# ------------------------------------------------------------ Reglas de borde
def test_money_rechaza_negativos_y_no_finitos():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("-0.01"))
    for valor in ("NaN", "Infinity"):
        with pytest.raises(InvalidOrderData):
            Money(Decimal(valor))


def test_money_no_suma_monedas_distintas():
    with pytest.raises(InvalidOrderData):
        Money(Decimal("10")).add(Money(Decimal("10"), "USD"))


def test_order_item_rechaza_cantidad_cero_negativa_y_sku_vacio():
    with pytest.raises(InvalidOrderData):
        OrderItem("SKU001", 0, Money(Decimal("10")))
    with pytest.raises(InvalidOrderData):
        OrderItem("SKU001", -1, Money(Decimal("10")))
    with pytest.raises(InvalidOrderData):
        OrderItem("  ", 1, Money(Decimal("10")))


def test_el_limite_cuenta_unidades_y_no_renglones():
    order = pedido_vip(20, "1")          # un solo renglon con 20 unidades: permitido
    assert len(order.items) == 1 and order.units == 20
    with pytest.raises(OrderItemLimitExceeded):
        order.add_item(OrderItem("SKU-U", 1, Money(Decimal("1"))))


def test_add_item_solo_en_draft_y_solo_mxn():
    order = pedido_vip(1, "100")
    with pytest.raises(InvalidOrderData):
        order.add_item(OrderItem("SKU-U", 1, Money(Decimal("1"), "USD")))
    order.confirm()
    with pytest.raises(InvalidOrderTransition):
        order.add_item(OrderItem("SKU-U", 1, Money(Decimal("1"))))


def test_prioridad_10_sobre_5_cuando_ambas_reglas_se_cumplen():
    order = pedido_vip(4, "1500")        # VIP, 4 unidades, total 6000 y sin promocion
    assert ten_percent.is_satisfied_by(order) and five_percent.is_satisfied_by(order)
    assert discount_rate(order) == Decimal("0.10")


def test_total_exactamente_5000_no_aplica_el_5_por_ciento():
    order = pedido_vip(1, "5000", vip=False)
    assert discount_rate(order) == Decimal("0")
    order_mas_un_centavo = pedido_vip(1, "5000.01", vip=False)
    assert discount_rate(order_mas_un_centavo) == Decimal("0.05")


def test_cancelar_desde_confirmed_exige_motivo_y_emite_evento():
    order = pedido_vip(1, "100")
    order.confirm()
    with pytest.raises(InvalidOrderData):
        order.cancel("  ")
    assert order.status == OrderStatus.CONFIRMED
    order.cancel("Cliente desistio")
    assert order.status == OrderStatus.CANCELLED
    assert nombres_eventos(order) == ["OrderConfirmed", "OrderCancelled"]


def test_deliver_y_return_solo_desde_shipped():
    order = pedido_vip(1, "100")
    order.confirm()
    with pytest.raises(InvalidOrderTransition):
        order.deliver()
    with pytest.raises(InvalidOrderTransition):
        order.return_order()


def test_estados_finales_no_admiten_mas_transiciones():
    order = pedido_vip(1, "100")
    order.confirm()
    order.ship("G-1")
    order.deliver()
    for accion in (order.confirm, lambda: order.ship("G-2"), lambda: order.cancel("x"),
                   order.deliver, order.return_order):
        with pytest.raises(InvalidOrderTransition):
            accion()
    assert order.status == OrderStatus.DELIVERED
