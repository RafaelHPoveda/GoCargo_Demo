from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from apps.branches.domain.entities.branch import Branch


@dataclass(frozen=True, kw_only=True)
class CreateBranchInput:
    name: str
    city: str
    max_weight_kg: Decimal
    is_active: bool = True


@dataclass(frozen=True, kw_only=True)
class UpdateBranchInput:
    """None indica un campo no enviado; los valores nulos se rechazan en HTTP."""

    name: str | None = None
    city: str | None = None
    max_weight_kg: Decimal | None = None
    is_active: bool | None = None


@dataclass(frozen=True, kw_only=True)
class BranchData:
    id: UUID
    name: str
    city: str
    max_weight_kg: Decimal
    is_active: bool

    @classmethod
    def from_entity(cls, branch: Branch) -> "BranchData":
        return cls(
            id=branch.id,
            name=branch.name,
            city=branch.city,
            max_weight_kg=branch.max_weight_kg,
            is_active=branch.is_active,
        )
