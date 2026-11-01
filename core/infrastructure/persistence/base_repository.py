from typing import Generic, Protocol, TypeVar
from uuid import UUID

from django.db import DatabaseError, IntegrityError, models

from core.application.exceptions import RepositoryConflictError, RepositoryError


T = TypeVar("T")
M = TypeVar("M", bound=models.Model)


class RepositoryMapper(Protocol[T, M]):
    """Conversión entre una entidad propia y un modelo ORM."""

    def to_model(self, entity: T) -> M:
        ...

    def to_domain(self, model: M) -> T:
        ...


class BaseRepository(Generic[T, M]):
    """Operaciones compartidas con Django ORM, sin SQL específico del motor."""

    def __init__(
        self,
        model: type[M],
        mapper: RepositoryMapper[T, M],
        db_alias: str = "default",
    ) -> None:
        self._model = model
        self._mapper = mapper
        self._db_alias = db_alias

    def save(self, entity: T) -> T:
        model_instance = self._mapper.to_model(entity)

        try:
            model_instance.save(using=self._db_alias, force_insert=True)
        except IntegrityError as exc:
            raise RepositoryConflictError(
                "La entidad no cumple las restricciones de persistencia."
            ) from exc
        except DatabaseError as exc:
            raise RepositoryError("No fue posible guardar la entidad.") from exc

        return self._mapper.to_domain(model_instance)

    def get_by_id(self, entity_id: UUID) -> T | None:
        try:
            model_instance = (
                self._model._default_manager.using(self._db_alias)
                .get(pk=entity_id)
            )
        except self._model.DoesNotExist:
            return None
        except DatabaseError as exc:
            raise RepositoryError("No fue posible consultar la entidad.") from exc

        return self._mapper.to_domain(model_instance)
