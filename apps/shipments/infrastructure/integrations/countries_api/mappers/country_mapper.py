from typing import Any

from apps.shipments.application.dto.country_data import CountryDataDTO
from apps.shipments.application.exceptions import CountryCatalogUnavailableError


class CountryGraphQLMapper:
    def to_dto(self, raw: Any, expected_code: str) -> CountryDataDTO:
        if not isinstance(raw, dict):
            raise CountryCatalogUnavailableError("Datos de país incompletos.")

        code = raw.get("code")
        name = raw.get("name")
        currency = raw.get("currency")
        if (
            not isinstance(code, str)
            or code != expected_code
            or not isinstance(name, str)
            or not name.strip()
            or len(name.strip()) > 200
            or not isinstance(currency, str)
            or not currency.strip()
            or len(currency.strip()) > 100
        ):
            raise CountryCatalogUnavailableError("El catálogo omitió datos obligatorios.")
        return CountryDataDTO(code=code, name=name.strip(), currency=currency.strip())
