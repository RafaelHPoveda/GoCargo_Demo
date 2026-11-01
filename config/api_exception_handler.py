from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.branches.application.exceptions import BranchNotFoundError
from apps.branches.domain.exceptions import BranchValidationError
from core.application.exceptions import RepositoryConflictError, RepositoryError


def api_exception_handler(exc, context):
    if isinstance(exc, BranchNotFoundError):
        return Response({"code": "branch_not_found", "detail": str(exc)}, status=404)
    if isinstance(exc, BranchValidationError):
        return Response({"code": "invalid_branch", "detail": str(exc)}, status=422)
    if isinstance(exc, RepositoryConflictError):
        return Response(
            {"code": "persistence_conflict", "detail": "Conflicto al guardar datos."},
            status=409,
        )
    if isinstance(exc, RepositoryError):
        return Response(
            {"code": "persistence_unavailable", "detail": "Persistencia no disponible."},
            status=503,
        )

    response = exception_handler(exc, context)
    if response is not None:
        original = response.data
        response.data = {
            "code": "invalid_request" if isinstance(exc, ValidationError) else "http_error",
            "detail": "Solicitud inválida." if isinstance(exc, ValidationError) else "Error HTTP.",
            "errors": original,
        }
    return response
