from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class BranchInfoDTO:
    id: UUID
    name: str
    is_active: bool
    max_weight_kg: Decimal
