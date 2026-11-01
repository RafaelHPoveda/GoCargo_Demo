from decimal import Decimal
from unittest import TestCase

from apps.shipments.domain.exceptions import InvalidWeightError
from apps.shipments.domain.value_objects.package_weight import PackageWeight


class PackageWeightTests(TestCase):
    def test_valid_boundaries(self):
        for value in ("0.01", "2.50", "50.00"):
            with self.subTest(value=value):
                self.assertEqual(PackageWeight(Decimal(value)).kg, Decimal(value))

    def test_invalid_weights_are_rejected(self):
        values = [
            Decimal("0"), Decimal("-1"), Decimal("50.01"),
            Decimal("NaN"), Decimal("Infinity"), Decimal("1.234"), 2.5,
        ]
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(InvalidWeightError):
                    PackageWeight(value)
