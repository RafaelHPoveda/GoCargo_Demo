from typing import Protocol

from apps.shipments.application.dto.country_data import CountryDataDTO


class ICountryCatalog(Protocol):
    def get_country(self, code: str) -> CountryDataDTO | None:
        """Devuelve datos, None por ausencia confirmada o lanza un fallo de catálogo."""
        ...
