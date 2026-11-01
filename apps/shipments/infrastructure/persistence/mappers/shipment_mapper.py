from apps.shipments.domain.entities.shipment import Shipment
from apps.shipments.domain.value_objects.package_weight import PackageWeight
from apps.shipments.infrastructure.persistence.models.shipment_model import ShipmentModel


class ShipmentMapper:
    def to_model(self, entity: Shipment) -> ShipmentModel:
        return ShipmentModel(
            id=entity.id,
            origin_branch_id=entity.origin_branch_id,
            origin_branch_name=entity.origin_branch_name,
            description=entity.description,
            weight_kg=entity.weight.kg,
            destination_country_code=entity.destination_country_code,
            destination_country_name=entity.destination_country_name,
            currency=entity.currency,
            status=entity.status,
        )

    def to_domain(self, model: ShipmentModel) -> Shipment:
        return Shipment(
            id=model.id,
            origin_branch_id=model.origin_branch_id,
            origin_branch_name=model.origin_branch_name,
            description=model.description,
            weight=PackageWeight(model.weight_kg),
            destination_country_code=model.destination_country_code,
            destination_country_name=model.destination_country_name,
            currency=model.currency,
            status=model.status,
        )
