from rest_framework.response import Response

from apps.shipments.application.exceptions import (
    BranchCapacityExceededError,
    BranchInactiveError,
    BranchNotFoundError,
    CountryCatalogUnavailableError,
    CountryNotFoundError,
    ShipmentNotFoundError,
)
from apps.shipments.domain.exceptions import ShipmentValidationError
from config.api_exception_handler import api_exception_handler


def shipment_exception_handler(exc, context):
    if isinstance(exc, ShipmentValidationError):
        return Response({"code": "invalid_shipment", "detail": str(exc)}, status=422)

    mappings = (
        (ShipmentNotFoundError, "shipment_not_found", 404),
        (BranchNotFoundError, "branch_not_found", 404),
        (BranchInactiveError, "branch_inactive", 422),
        (BranchCapacityExceededError, "branch_capacity_exceeded", 422),
        (CountryNotFoundError, "country_not_found", 404),
        (CountryCatalogUnavailableError, "country_catalog_unavailable", 503),
    )
    for exception_type, code, http_status in mappings:
        if isinstance(exc, exception_type):
            return Response({"code": code, "detail": str(exc)}, status=http_status)
    return api_exception_handler(exc, context)
