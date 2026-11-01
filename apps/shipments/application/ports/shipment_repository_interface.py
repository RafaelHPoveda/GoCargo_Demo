from typing import Protocol

from apps.shipments.domain.entities.shipment import Shipment
from core.application.ports.base_repository_interface import IBaseRepository


class IShipmentRepository(IBaseRepository[Shipment], Protocol):
    def list_all(self) -> list[Shipment]:
        ...
