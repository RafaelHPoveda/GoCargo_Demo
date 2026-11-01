

class RepositoryError(Exception):
    """No fue posible completar una operación de persistencia."""


class RepositoryConflictError(RepositoryError):
    """La escritura incumple una restricción de integridad."""