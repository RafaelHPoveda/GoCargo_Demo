from decimal import Decimal
from unittest.mock import Mock
from uuid import uuid4

from django.test import SimpleTestCase

from apps.branches.application.dto.branch_info_data import BranchInfoData
from apps.branches.application.interfaces.branch_service_interface import IBranchService
from apps.shipments.infrastructure.integrations.branches.local_branch_checker import (
    LocalBranchChecker,
)


class LocalBranchCheckerTests(SimpleTestCase):
    def test_adapter_uses_service_interface_and_maps_result(self):
        branch_id = uuid4()
        service = Mock(spec=IBranchService)
        service.get_info.return_value = BranchInfoData(
            id=branch_id, name="Managua", is_active=True, max_weight_kg=Decimal("25.00")
        )
        result = LocalBranchChecker(service).get_branch_info(branch_id)
        service.get_info.assert_called_once_with(branch_id)
        self.assertEqual(result.id, branch_id)
        self.assertEqual(result.max_weight_kg, Decimal("25.00"))

    def test_missing_branch_remains_none(self):
        service = Mock(spec=IBranchService)
        service.get_info.return_value = None
        self.assertIsNone(LocalBranchChecker(service).get_branch_info(uuid4()))
