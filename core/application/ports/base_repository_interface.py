from typing import Protocol, TypeVar
from uuid import UUID


T = TypeVar("T")


class IBaseRepository(Protocol[T]):
    """Contrato de persistencia independiente del motor de base de datos."""

    def save(self, entity: T) -> T:
        """Inserta una entidad nueva y devuelve su representación persistida."""
        ...

    def get_by_id(self, entity_id: UUID) -> T | None:
        """Devuelve la entidad o None cuando no existe."""
        ...