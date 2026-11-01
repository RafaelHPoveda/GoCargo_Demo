from apps.shipments.application.dto.country_data import CountryDataDTO
from apps.shipments.application.exceptions import CountryCatalogUnavailableError
from apps.shipments.infrastructure.integrations.countries_api.graphql_client import (
    CountryGraphQLClient,
)
from apps.shipments.infrastructure.integrations.countries_api.mappers.country_mapper import (
    CountryGraphQLMapper,
)
from apps.shipments.infrastructure.integrations.countries_api.queries.get_country import (
    GET_COUNTRY_QUERY,
)


class GraphQLCountryCatalog:
    def __init__(self, client: CountryGraphQLClient, mapper: CountryGraphQLMapper) -> None:
        self._client = client
        self._mapper = mapper

    def get_country(self, code: str) -> CountryDataDTO | None:
        data = self._client.execute(GET_COUNTRY_QUERY, {"code": code})
        if "country" not in data:
            raise CountryCatalogUnavailableError("La respuesta no contiene el país solicitado.")
        if data["country"] is None:
            return None
        return self._mapper.to_dto(data["country"], expected_code=code)
