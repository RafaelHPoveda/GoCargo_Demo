import uuid
from decimal import Decimal

from django.db import models


class BranchModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120)
    max_weight_kg = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "branches"
        ordering = ["name", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(max_weight_kg__gt=Decimal("0")),
                name="branch_capacity_positive",
            ),
        ]
