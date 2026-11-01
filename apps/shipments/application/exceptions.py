class ShipmentApplicationError(Exception):
    """No se puede completar una acción del servicio de envíos."""


class ShipmentNotFoundError(ShipmentApplicationError):
    """El envío solicitado no existe."""


class BranchNotFoundError(ShipmentApplicationError):
    """La sucursal solicitada no existe."""


class BranchInactiveError(ShipmentApplicationError):
    """La sucursal no está activa."""


class BranchCapacityExceededError(ShipmentApplicationError):
    """El peso supera la capacidad de la sucursal."""


class CountryNotFoundError(ShipmentApplicationError):
    """El catálogo confirmó que no existe el país."""


class CountryCatalogUnavailableError(ShipmentApplicationError):
    """El catálogo no pudo proporcionar una respuesta utilizable."""
