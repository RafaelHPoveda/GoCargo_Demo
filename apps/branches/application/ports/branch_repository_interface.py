from typing import Protocol

from apps.branches.domain.entities.branch import Branch
from core.application.ports.base_repository_interface import IBaseRepository


class IBranchRepository(IBaseRepository[Branch], Protocol):
    def update(self, entity: Branch) -> Branch | None:
        """Actualiza una sucursal existente; devuelve None si ya no existe."""
        ...

    def list_all(self) -> list[Branch]:
        ...
