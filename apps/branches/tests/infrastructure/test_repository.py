from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.test import TestCase

from apps.branches.domain.entities.branch import Branch
from apps.branches.infrastructure.persistence.repositories.branch_repository import (
    DjangoBranchRepository,
)
from core.application.exceptions import RepositoryConflictError


class BranchRepositoryTests(TestCase):
    def setUp(self):
        self.repository = DjangoBranchRepository()

    def test_round_trip_preserves_identity_and_decimal(self):
        branch = Branch(name="Managua", city="Managua", max_weight_kg=Decimal("25.25"))
        self.repository.save(branch)
        loaded = self.repository.get_by_id(branch.id)
        self.assertEqual(loaded, branch)
        self.assertIsInstance(loaded.max_weight_kg, Decimal)

    def test_missing_branch_returns_none(self):
        self.assertIsNone(self.repository.get_by_id(uuid4()))

    def test_duplicate_id_is_a_conflict_without_overwriting(self):
        branch = Branch(name="Original", city="Managua", max_weight_kg=Decimal("25.00"))
        self.repository.save(branch)
        with self.assertRaises(RepositoryConflictError):
            with transaction.atomic():
                self.repository.save(branch)
        self.assertEqual(self.repository.get_by_id(branch.id), branch)

    def test_list_returns_entities_in_stable_order(self):
        for name in ("Zeta", "Alfa"):
            self.repository.save(
                Branch(name=name, city="Managua", max_weight_kg=Decimal("25.00"))
            )
        self.assertEqual([branch.name for branch in self.repository.list_all()], ["Alfa", "Zeta"])
