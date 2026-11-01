from typing import Any

import requests

from apps.shipments.application.exceptions import CountryCatalogUnavailableError


class CountryGraphQLClient:
    def __init__(self, url: str, timeout: tuple[float, float]) -> None:
        self._url = url
        self._timeout = timeout

    def execute(self, query: str, variables: dict[str, str]) -> dict[str, Any]:
        try:
            response = requests.post(
                self._url,
                json={"query": query, "variables": variables},
                timeout=self._timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise CountryCatalogUnavailableError(
                "No fue posible consultar el catálogo de países."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CountryCatalogUnavailableError(
                "El catálogo devolvió una respuesta no válida."
            ) from exc

        if not isinstance(payload, dict) or "errors" in payload:
            raise CountryCatalogUnavailableError("El catálogo informó un error GraphQL.")
        data = payload.get("data")
        if not isinstance(data, dict):
            raise CountryCatalogUnavailableError("El catálogo no devolvió datos válidos.")
        return data
