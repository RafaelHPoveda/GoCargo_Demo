from typing import Protocol
from uuid import UUID

from apps.branches.application.dto.branch_data import (
    BranchData,
    CreateBranchInput,
    UpdateBranchInput,
)
from apps.branches.application.dto.branch_info_data import BranchInfoData


class IBranchService(Protocol):
    def create(self, data: CreateBranchInput) -> BranchData:
        ...

    def list_all(self) -> list[BranchData]:
        ...

    def update(self, branch_id: UUID, data: UpdateBranchInput) -> BranchData:
        ...

    def get_info(self, branch_id: UUID) -> BranchInfoData | None:
        ...
