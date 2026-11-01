class BranchValidationError(ValueError):
    """Una sucursal incumple sus reglas de negocio."""


class InvalidBranchNameError(BranchValidationError):
    """El nombre de sucursal es inválido."""


class InvalidBranchCityError(BranchValidationError):
    """La ciudad de sucursal es inválida."""


class InvalidBranchCapacityError(BranchValidationError):
    """La capacidad de sucursal es inválida."""