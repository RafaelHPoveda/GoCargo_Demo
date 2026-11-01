from apps.branches.domain.entities.branch import Branch
from apps.branches.infrastructure.persistence.models.branch_model import BranchModel


class BranchMapper:
    def to_model(self, entity: Branch) -> BranchModel:
        return BranchModel(
            id=entity.id,
            name=entity.name,
            city=entity.city,
            max_weight_kg=entity.max_weight_kg,
            is_active=entity.is_active,
        )

    def to_domain(self, model: BranchModel) -> Branch:
        return Branch(
            id=model.id,
            name=model.name,
            city=model.city,
            max_weight_kg=model.max_weight_kg,
            is_active=model.is_active,
        )
