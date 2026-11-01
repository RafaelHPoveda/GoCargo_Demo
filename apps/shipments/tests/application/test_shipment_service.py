from dataclasses import replace
from decimal import Decimal
from unittest import TestCase
from unittest.mock import MagicMock, Mock
from uuid import uuid4

from apps.shipments.application.dto.branch_info_data import BranchInfoDTO
from apps.shipments.application.dto.country_data import CountryDataDTO
from apps.shipments.application.dto.shipment_data import CreateShipmentInput
from apps.shipments.application.exceptions import (
    BranchCapacityExceededError,
    BranchInactiveError,
    BranchNotFoundError,
    CountryCatalogUnavailableError,
    CountryNotFoundError,
    ShipmentNotFoundError,
)
from apps.shipments.application.interfaces.shipment_service_interface import IShipmentService
from apps.shipments.application.services.shipment_service import ShipmentService
from apps.shipments.domain.exceptions import InvalidWeightError
from core.application.exceptions import RepositoryError
from apps.shipments.tests.helpers import make_shipment


class ShipmentServiceTests(TestCase):
    def setUp(self):
        self.branch = BranchInfoDTO(
            id=uuid4(), name="Managua", is_active=True, max_weight_kg=Decimal("25.00")
        )
        self.data = CreateShipmentInput(
            origin_branch_id=self.branch.id,
            description="Documentos",
            weight_kg=Decimal("2.50"),
            destination_country_code="cr",
        )
        self.repository = Mock()
        self.repository.save.side_effect = lambda entity: entity
        self.checker = Mock()
        self.checker.get_branch_info.return_value = self.branch
        self.catalog = Mock()
        self.catalog.get_country.return_value = CountryDataDTO(
            code="CR", name="Costa Rica", currency="CRC"
        )
        self.unit_of_work = MagicMock()
        self.unit_of_work.__exit__.return_value = False
        self.service: IShipmentService = ShipmentService(
            self.repository, self.checker, self.catalog, self.unit_of_work
        )

    def test_success_preserves_snapshots_and_exits_transaction_before_return(self):
        result = self.service.create(self.data)
        self.assertEqual(result.origin_branch_name, "Managua")
        self.assertEqual(result.currency, "CRC")
        self.assertEqual(result.weight_kg, Decimal("2.50"))
        self.assertEqual(result.status, "CREATED")
        self.catalog.get_country.assert_called_once_with("CR")
        self.repository.save.assert_called_once()
        self.unit_of_work.__enter__.assert_called_once()
        self.unit_of_work.__exit__.assert_called_once_with(None, None, None)

    def test_invalid_weight_never_calls_ports(self):
        with self.assertRaises(InvalidWeightError):
            self.service.create(replace(self.data, weight_kg=Decimal("51")))
        self.checker.get_branch_info.assert_not_called()
        self.catalog.get_country.assert_not_called()
        self.repository.save.assert_not_called()
        self.unit_of_work.__enter__.assert_not_called()

    def test_missing_branch_stops_before_country(self):
        self.checker.get_branch_info.return_value = None
        with self.assertRaises(BranchNotFoundError):
            self.service.create(self.data)
        self.catalog.get_country.assert_not_called()
        self.repository.save.assert_not_called()

    def test_inactive_branch_stops_before_country(self):
        self.checker.get_branch_info.return_value = replace(self.branch, is_active=False)
        with self.assertRaises(BranchInactiveError):
            self.service.create(self.data)
        self.catalog.get_country.assert_not_called()
        self.repository.save.assert_not_called()

    def test_capacity_limit_stops_before_country(self):
        with self.assertRaises(BranchCapacityExceededError):
            self.service.create(replace(self.data, weight_kg=Decimal("30")))
        self.catalog.get_country.assert_not_called()
        self.repository.save.assert_not_called()

    def test_missing_country_never_starts_transaction(self):
        self.catalog.get_country.return_value = None
        with self.assertRaises(CountryNotFoundError):
            self.service.create(self.data)
        self.unit_of_work.__enter__.assert_not_called()
        self.repository.save.assert_not_called()

    def test_catalog_failure_never_starts_transaction(self):
        self.catalog.get_country.side_effect = CountryCatalogUnavailableError("No disponible")
        with self.assertRaises(CountryCatalogUnavailableError):
            self.service.create(self.data)
        self.unit_of_work.__enter__.assert_not_called()
        self.repository.save.assert_not_called()

    def test_repository_failure_reaches_unit_of_work_exit(self):
        self.repository.save.side_effect = RepositoryError("No disponible")
        with self.assertRaises(RepositoryError):
            self.service.create(self.data)
        exit_args = self.unit_of_work.__exit__.call_args.args
        self.assertIs(exit_args[0], RepositoryError)

    def test_list_reads_local_data_without_other_dependencies(self):
        shipment = make_shipment()
        self.repository.list_all.return_value = [shipment]
        results = self.service.list_all()
        self.assertEqual(results[0].id, shipment.id)
        self.catalog.get_country.assert_not_called()
        self.checker.get_branch_info.assert_not_called()
        self.unit_of_work.__enter__.assert_not_called()

    def test_get_by_id_reads_local_data_without_catalog(self):
        shipment = make_shipment()
        self.repository.get_by_id.return_value = shipment
        self.assertEqual(self.service.get_by_id(shipment.id).id, shipment.id)
        self.repository.get_by_id.assert_called_once_with(shipment.id)
        self.catalog.get_country.assert_not_called()

    def test_missing_shipment_raises_not_found(self):
        self.repository.get_by_id.return_value = None
        with self.assertRaises(ShipmentNotFoundError):
            self.service.get_by_id(uuid4())
