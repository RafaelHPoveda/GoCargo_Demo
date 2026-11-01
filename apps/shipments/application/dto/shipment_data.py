from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from apps.shipments.domain.entities.shipment import Shipment


@dataclass(frozen=True, kw_only=True)
class CreateShipmentInput:
    origin_branch_id: UUID
    description: str
    weight_kg: Decimal
    destination_country_code: str


@dataclass(frozen=True, kw_only=True)
class ShipmentData:
    id: UUID
    origin_branch_id: UUID
    origin_branch_name: str
    description: str
    weight_kg: Decimal
    destination_country_code: str
    destination_country_name: str
    currency: str
    status: str

    @classmethod
    def from_entity(cls, shipment: Shipment) -> "ShipmentData":
        return cls(
            id=shipment.id,
            origin_branch_id=shipment.origin_branch_id,
            origin_branch_name=shipment.origin_branch_name,
            description=shipment.description,
            weight_kg=shipment.weight.kg,
            destination_country_code=shipment.destination_country_code,
            destination_country_name=shipment.destination_country_name,
            currency=shipment.currency,
            status=shipment.status,
        )
