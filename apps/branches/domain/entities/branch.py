from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from apps.branches.domain.exceptions import (
    InvalidBranchCapacityError,
    InvalidBranchCityError,
    InvalidBranchNameError,
)


@dataclass(frozen=True, kw_only=True)
class Branch:
    name: str
    city: str
    max_weight_kg: Decimal
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        name = self.name.strip()
        city = self.city.strip()
        if not name or len(name) > 200:
            raise InvalidBranchNameError("El nombre debe tener entre 1 y 200 caracteres.")
        if not city or len(city) > 120:
            raise InvalidBranchCityError("La ciudad debe tener entre 1 y 120 caracteres.")

        capacity = self.max_weight_kg
        if (
            not isinstance(capacity, Decimal)
            or not capacity.is_finite()
            or capacity <= 0
            or capacity > Decimal("999999.99")
            or capacity != capacity.quantize(Decimal("0.01"))
        ):
            raise InvalidBranchCapacityError(
                "La capacidad debe ser positiva, de hasta 999999.99 kg y dos decimales."
            )

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "city", city)
