from uuid import UUID

from apps.branches.application.interfaces.branch_service_interface import IBranchService
from apps.shipments.application.dto.branch_info_data import BranchInfoDTO


class LocalBranchChecker:
    def __init__(self, service: IBranchService) -> None:
        self._service = service

    def get_branch_info(self, branch_id: UUID) -> BranchInfoDTO | None:
        branch = self._service.get_info(branch_id)
        if branch is None:
            return None
        return BranchInfoDTO(
            id=branch.id,
            name=branch.name,
            is_active=branch.is_active,
            max_weight_kg=branch.max_weight_kg,
        )
