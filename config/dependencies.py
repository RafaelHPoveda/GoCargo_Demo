from django.conf import settings

from apps.branches.application.interfaces.branch_service_interface import IBranchService
from apps.branches.application.services.branch_service import BranchService
from apps.branches.infrastructure.persistence.repositories.branch_repository import (
    DjangoBranchRepository,
)
from apps.shipments.application.interfaces.shipment_service_interface import IShipmentService
from apps.shipments.application.services.shipment_service import ShipmentService
from apps.shipments.infrastructure.integrations.branches.local_branch_checker import (
    LocalBranchChecker,
)
from apps.shipments.infrastructure.integrations.countries_api.country_catalog import (
    GraphQLCountryCatalog,
)
from apps.shipments.infrastructure.integrations.countries_api.graphql_client import (
    CountryGraphQLClient,
)
from apps.shipments.infrastructure.integrations.countries_api.mappers.country_mapper import (
    CountryGraphQLMapper,
)
from apps.shipments.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from apps.shipments.infrastructure.persistence.repositories.shipment_repository import (
    DjangoShipmentRepository,
)


def build_branch_repository() -> DjangoBranchRepository:
    return DjangoBranchRepository(db_alias="default")


def build_branch_service() -> IBranchService:
    return BranchService(build_branch_repository())


def build_country_catalog() -> GraphQLCountryCatalog:
    client = CountryGraphQLClient(
        url=settings.COUNTRIES_API_URL,
        timeout=(settings.COUNTRIES_CONNECT_TIMEOUT, settings.COUNTRIES_READ_TIMEOUT),
    )
    return GraphQLCountryCatalog(client, CountryGraphQLMapper())


def build_shipment_service() -> IShipmentService:
    db_alias = "default"
    return ShipmentService(
        repository=DjangoShipmentRepository(db_alias=db_alias),
        branch_checker=LocalBranchChecker(build_branch_service()),
        country_catalog=build_country_catalog(),
        unit_of_work=DjangoUnitOfWork(db_alias=db_alias),
    )
