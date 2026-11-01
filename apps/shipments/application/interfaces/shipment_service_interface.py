from typing import Protocol
from uuid import UUID

from apps.shipments.application.dto.shipment_data import CreateShipmentInput, ShipmentData


class IShipmentService(Protocol):
    def list_all(self) -> list[ShipmentData]:
        ...

    def get_by_id(self, shipment_id: UUID) -> ShipmentData:
        ...

    def create(self, data: CreateShipmentInput) -> ShipmentData:
        ...
