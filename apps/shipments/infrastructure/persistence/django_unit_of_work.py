from types import TracebackType
from typing import Literal, Self

from django.db import DatabaseError, transaction
from django.db.transaction import Atomic

from core.application.exceptions import RepositoryError


class DjangoUnitOfWork:
    def __init__(self, db_alias: str = "default") -> None:
        self._db_alias = db_alias
        self._atomic: Atomic | None = None

    def __enter__(self) -> Self:
        if self._atomic is not None:
            raise RuntimeError("La unidad de trabajo ya está activa.")
        atomic = transaction.atomic(using=self._db_alias)
        try:
            atomic.__enter__()
        except DatabaseError as exc:
            raise RepositoryError("No fue posible iniciar la transacción.") from exc
        self._atomic = atomic
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        if self._atomic is None:
            raise RuntimeError("La unidad de trabajo no está activa.")
        atomic = self._atomic
        self._atomic = None
        try:
            atomic.__exit__(exc_type, exc_value, traceback)
        except DatabaseError as exc:
            raise RepositoryError("No fue posible finalizar la transacción.") from exc
        return False
