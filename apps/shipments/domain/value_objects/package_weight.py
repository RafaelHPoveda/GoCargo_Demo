from dataclasses import dataclass
from decimal import Decimal

from apps.shipments.domain.exceptions import InvalidWeightError


@dataclass(frozen=True)
class PackageWeight:
    kg: Decimal

    def __post_init__(self) -> None:
        if (
            not isinstance(self.kg, Decimal)
            or not self.kg.is_finite()
            or self.kg <= 0
            or self.kg > Decimal("50.00")
            or self.kg != self.kg.quantize(Decimal("0.01"))
        ):
            raise InvalidWeightError(
                "El peso debe ser mayor que cero, de hasta 50 kg y dos decimales."
            )
