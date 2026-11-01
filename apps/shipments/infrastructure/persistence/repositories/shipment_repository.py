from django.db import DatabaseError

from apps.shipments.domain.entities.shipment import Shipment
from apps.shipments.infrastructure.persistence.mappers.shipment_mapper import ShipmentMapper
from apps.shipments.infrastructure.persistence.models.shipment_model import ShipmentModel
from core.infrastructure.persistence.base_repository import BaseRepository
from core.application.exceptions import RepositoryError


class DjangoShipmentRepository(BaseRepository[Shipment, ShipmentModel]):
    def __init__(self, db_alias: str = "default") -> None:
        super().__init__(ShipmentModel, ShipmentMapper(), db_alias)

    def list_all(self) -> list[Shipment]:
        try:
            records = list(
                self._model._default_manager.using(self._db_alias).order_by("id")
            )
        except DatabaseError as exc:
            raise RepositoryError("No fue posible listar envíos.") from exc
        return [self._mapper.to_domain(record) for record in records]
