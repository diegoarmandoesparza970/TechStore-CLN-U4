from decimal import Decimal


# --- CLASES BASE DEL PATRÓN SPECIFICATION ---
class Specification:
    def is_satisfied_by(self, order):
        raise NotImplementedError

    def __and__(self, other):
        return AndSpec(self, other)

    def __or__(self, other):
        return OrSpec(self, other)

    def __invert__(self):
        return NotSpec(self)


class AndSpec(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order):
        return self.left.is_satisfied_by(order) and self.right.is_satisfied_by(order)


class OrSpec(Specification):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def is_satisfied_by(self, order):
        return self.left.is_satisfied_by(order) or self.right.is_satisfied_by(order)


class NotSpec(Specification):
    def __init__(self, spec):
        self.spec = spec

    def is_satisfied_by(self, order):
        return not self.spec.is_satisfied_by(order)


# --- REGLAS DE NEGOCIO ESPECÍFICAS DE TECHSTORE ---

class MinimumAmountSpec(Specification):
    def __init__(self, amount: Decimal):
        self.amount = amount

    def is_satisfied_by(self, order):
        # La guía exige > (mayor estricto), no >=
        return order.total.amount > self.amount


class VIPCustomerSpec(Specification):
    def is_satisfied_by(self, order):
        return order.customer.is_vip


class MinimumUnitsSpec(Specification):
    def __init__(self, units: int):
        self.units = units

    def is_satisfied_by(self, order):
        return order.units >= self.units


class ActivePromotionSpec(Specification):
    def is_satisfied_by(self, order):
        return order.has_promotion


# --- COMBINACIÓN DE REGLAS (Ejemplo de uso) ---
# Regla de descuento del 10 %
ten_percent = (
        MinimumAmountSpec(Decimal("500"))
        & VIPCustomerSpec()
        & MinimumUnitsSpec(4)
        & ~ActivePromotionSpec()
)

# Regla de descuento del 5 %
five_percent = (
        MinimumAmountSpec(Decimal("5000"))
        & ~ActivePromotionSpec()
)


def discount_rate(order) -> Decimal:
    """Tasa de descuento aplicable. Se evalua primero el 10 % y despues el 5 %,
    de modo que cuando ambas reglas se cumplen gana la del 10 %."""
    if ten_percent.is_satisfied_by(order):
        return Decimal("0.10")
    if five_percent.is_satisfied_by(order):
        return Decimal("0.05")
    return Decimal("0")
