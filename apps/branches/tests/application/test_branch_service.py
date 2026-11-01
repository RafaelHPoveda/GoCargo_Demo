from decimal import Decimal
from unittest import TestCase
from unittest.mock import Mock
from uuid import uuid4

from apps.branches.application.dto.branch_data import CreateBranchInput, UpdateBranchInput
from apps.branches.application.exceptions import BranchNotFoundError
from apps.branches.application.interfaces.branch_service_interface import IBranchService
from apps.branches.application.ports.branch_repository_interface import IBranchRepository
from apps.branches.application.services.branch_service import BranchService
from apps.branches.domain.entities.branch import Branch
from apps.branches.domain.exceptions import InvalidBranchCapacityError


class BranchServiceTests(TestCase):
    def setUp(self):
        self.repository = Mock(spec=IBranchRepository)
        self.repository.save.side_effect = lambda entity: entity
        self.service: IBranchService = BranchService(self.repository)

    def test_create_validates_and_returns_dto(self):
        result = self.service.create(
            CreateBranchInput(name="Managua", city="Managua", max_weight_kg=Decimal("25.00"))
        )
        self.assertEqual(result.name, "Managua")
        self.repository.save.assert_called_once()
        self.assertEqual(self.repository.save.call_args.args[0].id, result.id)

    def test_invalid_branch_never_calls_repository(self):
        with self.assertRaises(InvalidBranchCapacityError):
            self.service.create(
                CreateBranchInput(name="Managua", city="Managua", max_weight_kg=Decimal("0"))
            )
        self.repository.save.assert_not_called()

    def test_list_and_get_info_return_own_dtos(self):
        branch = Branch(name="Managua", city="Managua", max_weight_kg=Decimal("25.00"))
        self.repository.list_all.return_value = [branch]
        self.repository.get_by_id.return_value = branch
        self.assertEqual(self.service.list_all()[0].id, branch.id)
        self.assertEqual(self.service.get_info(branch.id).max_weight_kg, Decimal("25.00"))
        self.repository.get_by_id.assert_called_once_with(branch.id)

    def test_get_info_returns_none_for_missing_branch(self):
        self.repository.get_by_id.return_value = None
        self.assertIsNone(self.service.get_info(uuid4()))

    def test_update_validates_and_preserves_identity(self):
        branch = Branch(name="Managua", city="Managua", max_weight_kg=Decimal("25.00"))
        self.repository.get_by_id.return_value = branch
        self.repository.update.side_effect = lambda entity: entity
        result = self.service.update(branch.id, UpdateBranchInput(is_active=False))
        self.assertEqual(result.id, branch.id)
        self.assertFalse(result.is_active)
        self.assertEqual(result.name, branch.name)

    def test_invalid_update_never_writes(self):
        branch = Branch(name="Managua", city="Managua", max_weight_kg=Decimal("25.00"))
        self.repository.get_by_id.return_value = branch
        with self.assertRaises(InvalidBranchCapacityError):
            self.service.update(branch.id, UpdateBranchInput(max_weight_kg=Decimal("0")))
        self.repository.update.assert_not_called()

    def test_update_missing_branch_never_writes(self):
        self.repository.get_by_id.return_value = None
        with self.assertRaises(BranchNotFoundError):
            self.service.update(uuid4(), UpdateBranchInput(name="Otro"))
        self.repository.update.assert_not_called()

    def test_branch_deleted_before_write_returns_not_found(self):
        branch = Branch(name="Managua", city="Managua", max_weight_kg=Decimal("25.00"))
        self.repository.get_by_id.return_value = branch
        self.repository.update.return_value = None
        with self.assertRaises(BranchNotFoundError):
            self.service.update(branch.id, UpdateBranchInput(name="Otro"))
