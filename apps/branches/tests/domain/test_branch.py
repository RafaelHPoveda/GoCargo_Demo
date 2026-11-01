from dataclasses import FrozenInstanceError
from decimal import Decimal
from unittest import TestCase

from apps.branches.domain.entities.branch import Branch
from apps.branches.domain.exceptions import BranchValidationError


class BranchTests(TestCase):
    def test_valid_branch_normalizes_text_and_generates_identity(self):
        first = Branch(name=" Managua ", city=" Managua ", max_weight_kg=Decimal("25.00"))
        second = Branch(name="Managua", city="Managua", max_weight_kg=Decimal("25.00"))
        self.assertEqual(first.name, "Managua")
        self.assertNotEqual(first.id, second.id)
        with self.assertRaises(FrozenInstanceError):
            first.name = "Otro nombre"

    def test_invalid_name_city_or_capacity_is_rejected(self):
        cases = [
            {"name": "   "},
            {"city": ""},
            {"max_weight_kg": Decimal("0")},
            {"max_weight_kg": Decimal("-1")},
            {"max_weight_kg": Decimal("NaN")},
            {"max_weight_kg": Decimal("Infinity")},
            {"max_weight_kg": Decimal("1.234")},
        ]
        for changes in cases:
            data = {"name": "Managua", "city": "Managua", "max_weight_kg": Decimal("25.00")}
            data.update(changes)
            with self.subTest(changes=changes):
                with self.assertRaises(BranchValidationError):
                    Branch(**data)
