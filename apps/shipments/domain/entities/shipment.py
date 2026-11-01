from dataclasses import dataclass, field
from uuid import UUID, uuid4

from apps.shipments.domain.exceptions import InvalidShipmentError
from apps.shipments.domain.value_objects.package_weight import PackageWeight


@dataclass(frozen=True, kw_only=True)
class Shipment:
    origin_branch_id: UUID
    origin_branch_name: str
    description: str
    weight: PackageWeight
    destination_country_code: str
    destination_country_name: str
    currency: str
    status: str = "CREATED"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        description = self.description.strip()
        code = self.destination_country_code.strip().upper()
        if not description or len(description) > 500:
            raise InvalidShipmentError("La descripción debe tener entre 1 y 500 caracteres.")
        if len(code) != 2 or not code.isascii() or not code.isalpha():
            raise InvalidShipmentError("El país debe tener un código de dos letras.")
        if not self.origin_branch_name.strip() or len(self.origin_branch_name) > 200:
            raise InvalidShipmentError("Nombre de sucursal inválido.")
        if not self.destination_country_name.strip() or len(self.destination_country_name) > 200:
            raise InvalidShipmentError("Nombre de país inválido.")
        if not self.currency.strip() or len(self.currency) > 100:
            raise InvalidShipmentError("La información de moneda es obligatoria.")
        if not isinstance(self.weight, PackageWeight) or self.status != "CREATED":
            raise InvalidShipmentError("Peso o estado del envío inválidos.")
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "destination_country_code", code)
