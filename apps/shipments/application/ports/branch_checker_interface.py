from typing import Protocol
from uuid import UUID

from apps.shipments.application.dto.branch_info_data import BranchInfoDTO


class IBranchChecker(Protocol):
    def get_branch_info(self, branch_id: UUID) -> BranchInfoDTO | None:
        ...
