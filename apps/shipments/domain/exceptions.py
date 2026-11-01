class ShipmentValidationError(ValueError):
    """Una regla del dominio de envíos no se cumple."""


class InvalidWeightError(ShipmentValidationError):
    """Peso fuera del rango o precisión permitidos."""


class InvalidShipmentError(ShipmentValidationError):
    """Datos de un envío inconsistentes."""
