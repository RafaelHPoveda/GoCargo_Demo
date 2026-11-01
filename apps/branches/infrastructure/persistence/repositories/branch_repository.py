from django.db import DatabaseError, IntegrityError

from apps.branches.domain.entities.branch import Branch
from apps.branches.infrastructure.persistence.mappers.branch_mapper import BranchMapper
from apps.branches.infrastructure.persistence.models.branch_model import BranchModel
from core.application.exceptions import RepositoryConflictError, RepositoryError
from core.infrastructure.persistence.base_repository import BaseRepository


class DjangoBranchRepository(BaseRepository[Branch, BranchModel]):
    def __init__(self, db_alias: str = "default") -> None:
        super().__init__(BranchModel, BranchMapper(), db_alias)

    def list_all(self) -> list[Branch]:
        try:
            records = list(
                self._model._default_manager.using(self._db_alias).order_by("name", "id")
            )
        except DatabaseError as exc:
            raise RepositoryError("No fue posible listar sucursales.") from exc
        return [self._mapper.to_domain(record) for record in records]

    def update(self, entity: Branch) -> Branch | None:
        try:
            affected = self._model._default_manager.using(self._db_alias).filter(
                pk=entity.id
            ).update(
                name=entity.name,
                city=entity.city,
                max_weight_kg=entity.max_weight_kg,
                is_active=entity.is_active,
            )
        except IntegrityError as exc:
            raise RepositoryConflictError(
                "La sucursal no cumple las restricciones de persistencia."
            ) from exc
        except DatabaseError as exc:
            raise RepositoryError("No fue posible actualizar la sucursal.") from exc
        return entity if affected else None
