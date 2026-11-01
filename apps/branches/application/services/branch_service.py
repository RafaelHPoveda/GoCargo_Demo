from dataclasses import replace
from uuid import UUID

from apps.branches.application.dto.branch_data import (
    BranchData,
    CreateBranchInput,
    UpdateBranchInput,
)
from apps.branches.application.exceptions import BranchNotFoundError
from apps.branches.application.dto.branch_info_data import BranchInfoData
from apps.branches.application.interfaces.branch_service_interface import IBranchService
from apps.branches.application.ports.branch_repository_interface import IBranchRepository
from apps.branches.domain.entities.branch import Branch


class BranchService(IBranchService):
    def __init__(self, repository: IBranchRepository) -> None:
        self._repository = repository

    def create(self, data: CreateBranchInput) -> BranchData:
        branch = Branch(
            name=data.name,
            city=data.city,
            max_weight_kg=data.max_weight_kg,
            is_active=data.is_active,
        )
        saved = self._repository.save(branch)
        return BranchData.from_entity(saved)

    def list_all(self) -> list[BranchData]:
        return [BranchData.from_entity(branch) for branch in self._repository.list_all()]

    def update(self, branch_id: UUID, data: UpdateBranchInput) -> BranchData:
        branch = self._repository.get_by_id(branch_id)
        if branch is None:
            raise BranchNotFoundError("La sucursal no existe.")
        changes = {
            field: value
            for field in ("name", "city", "max_weight_kg", "is_active")
            if (value := getattr(data, field)) is not None
        }
        updated = replace(branch, **changes)
        saved = self._repository.update(updated)
        if saved is None:
            raise BranchNotFoundError("La sucursal no existe.")
        return BranchData.from_entity(saved)

    def get_info(self, branch_id: UUID) -> BranchInfoData | None:
        branch = self._repository.get_by_id(branch_id)
        if branch is None:
            return None
        return BranchInfoData(
            id=branch.id,
            name=branch.name,
            is_active=branch.is_active,
            max_weight_kg=branch.max_weight_kg,
        )
