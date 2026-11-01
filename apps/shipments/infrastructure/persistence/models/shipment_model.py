import uuid
from decimal import Decimal

from django.db import models


class ShipmentModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    origin_branch_id = models.UUIDField()
    origin_branch_name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    destination_country_code = models.CharField(max_length=2)
    destination_country_name = models.CharField(max_length=200)
    currency = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default="CREATED")

    class Meta:
        db_table = "shipments"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(weight_kg__gt=Decimal("0"))
                & models.Q(weight_kg__lte=Decimal("50.00")),
                name="shipment_weight_valid",
            ),
        ]
