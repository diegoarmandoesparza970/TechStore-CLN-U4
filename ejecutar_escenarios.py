from cargar_csv import load_fixture
from app.domain import InvalidOrderData, InvalidOrderTransition, OrderItemLimitExceeded, OrderItem, Money
from decimal import Decimal
from app.specifications import discount_rate
import os


def pct(order):
    """Evalua las Specifications del pedido y devuelve la tasa como texto (p. ej. '10%')."""
    return f"{int(discount_rate(order) * 100)}%"


def celda(texto):
    """Escapa el caracter | para que no rompa las columnas de la tabla Markdown."""
    return str(texto).replace("|", "\\|")


def fmt_ev(order):
    return ", ".join([e.name for e in order.events]) if order.events else "(ninguno)"


def ejecutar():
    orders = load_fixture()
    resultados = []

    def log(caso, order_id, operacion, res, order):
        linea = f"{caso} {order_id}: OK   | {operacion} -> {res}. Estado final: {order.status.value} | eventos={fmt_ev(order)}"
        print(linea)
        resultados.append({
            "caso": caso,
            "pedido": order_id,
            "operacion": operacion,
            "resultado": res,
            "estado": order.status.value,
            "eventos": fmt_ev(order),
        })

    # E01
    o = orders["O001"]
    log("E01", "O001", "evaluar_descuento", pct(o), o)

    # E02
    o = orders["O002"]
    log("E02", "O002", "evaluar_descuento", pct(o), o)

    # E03
    o = orders["O003"]
    try:
        o.confirm()
    except InvalidOrderData as e:
        log("E03", "O003", "confirm()", f"InvalidOrderData: {e}", o)

    # E04
    o = orders["O005"]
    log("E04", "O005", "evaluar_descuento", pct(o), o)

    # E05
    o = orders["O006"]
    log("E05", "O006", "evaluar_descuento", pct(o), o)

    # E06
    o = orders["O007"]
    try:
        o.confirm()
    except InvalidOrderData as e:
        log("E06", "O007", "confirm()", f"InvalidOrderData: {e}", o)

    # E07
    o = orders["O008"]
    o.confirm()
    log("E07", "O008", "confirm()", "OK", o)

    # E08
    o = orders["O009"]
    try:
        o.add_item(OrderItem("SKU003", 2, Money(Decimal("100"))))
    except OrderItemLimitExceeded as e:
        log("E08", "O009", "add_item(SKU003 x2)", f"OrderItemLimitExceeded: {e}", o)

    # E09
    o = orders["O010"]
    log("E09", "O010", "evaluar_descuento", pct(o), o)

    # E10
    o = orders["O011"]
    log("E10", "O011", "evaluar_descuento", pct(o), o)

    # E11
    o = orders["O012"]
    o.confirm()
    try:
        o.ship("")
    except InvalidOrderData as e:
        log("E11", "O012", "confirm() -> OK; ship('')", f"InvalidOrderData: {e}", o)

    # E12
    o = orders["O013"]
    o.confirm()
    try:
        o.confirm()
    except InvalidOrderTransition as e:
        log("E12", "O013", "confirm() -> OK; confirm() (2a vez)", f"InvalidOrderTransition: {e}", o)

    # E13
    o = orders["O014"]
    o.confirm()
    o.ship("GUIA-014")
    try:
        o.cancel("Ya no lo quiero")
    except InvalidOrderTransition as e:
        log("E13", "O014", "confirm()-> OK; ship('GUIA-014')-> OK; cancel('Ya no lo quiero')",
            f"InvalidOrderTransition: {e}", o)

    # E14
    o = orders["O015"]
    o.confirm()
    o.ship("GUIA-015")
    o.return_order()
    log("E14", "O015", "confirm()-> OK; ship('GUIA-015')-> OK; return_order()", "OK", o)

    # E15
    o = orders["O016"]
    o.confirm()
    o.ship("GUIA-016")
    o.deliver()
    log("E15", "O016", "confirm()-> OK; ship('GUIA-016')-> OK; deliver()", "OK", o)

    # Exportar bitácora (tabla en Markdown)
    os.makedirs("docs", exist_ok=True)
    ruta = os.path.join("docs", "bitacora_escenarios.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# Bitácora de Escenarios\n\n")
        f.write("| Caso | Pedido | Operación | Resultado | Estado final | Eventos |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for r in resultados:
            celdas = [r["caso"], r["pedido"], f"`{r['operacion']}`", celda(r["resultado"]),
                      r["estado"], celda(r["eventos"])]
            f.write("| " + " | ".join(celdas) + " |\n")
    print(f"\nBitácora escrita en {os.path.abspath(ruta)}")


if __name__ == "__main__":
    ejecutar()