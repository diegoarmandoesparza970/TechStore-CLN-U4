# Bitácora de Escenarios

| Caso | Pedido | Operación | Resultado | Estado final | Eventos |
| --- | --- | --- | --- | --- | --- |
| E01 | O001 | `evaluar_descuento` | 10% | DRAFT | (ninguno) |
| E02 | O002 | `evaluar_descuento` | 0% | DRAFT | (ninguno) |
| E03 | O003 | `confirm()` | InvalidOrderData: Requiere artículos y cliente activo para confirmarse | DRAFT | (ninguno) |
| E04 | O005 | `evaluar_descuento` | 0% | DRAFT | (ninguno) |
| E05 | O006 | `evaluar_descuento` | 5% | DRAFT | (ninguno) |
| E06 | O007 | `confirm()` | InvalidOrderData: Requiere artículos y cliente activo para confirmarse | DRAFT | (ninguno) |
| E07 | O008 | `confirm()` | OK | CONFIRMED | OrderConfirmed |
| E08 | O009 | `add_item(SKU003 x2)` | OrderItemLimitExceeded: Máximo 20 unidades | DRAFT | (ninguno) |
| E09 | O010 | `evaluar_descuento` | 0% | DRAFT | (ninguno) |
| E10 | O011 | `evaluar_descuento` | 0% | DRAFT | (ninguno) |
| E11 | O012 | `confirm() -> OK; ship('')` | InvalidOrderData: El envío requiere un número de guía | CONFIRMED | OrderConfirmed |
| E12 | O013 | `confirm() -> OK; confirm() (2a vez)` | InvalidOrderTransition: Solo se puede confirmar un pedido DRAFT | CONFIRMED | OrderConfirmed |
| E13 | O014 | `confirm()-> OK; ship('GUIA-014')-> OK; cancel('Ya no lo quiero')` | InvalidOrderTransition: Solo se puede cancelar un pedido CONFIRMED | SHIPPED | OrderConfirmed, OrderShipped |
| E14 | O015 | `confirm()-> OK; ship('GUIA-015')-> OK; return_order()` | OK | RETURNED | OrderConfirmed, OrderShipped, OrderReturned |
| E15 | O016 | `confirm()-> OK; ship('GUIA-016')-> OK; deliver()` | OK | DELIVERED | OrderConfirmed, OrderShipped, OrderDelivered |
