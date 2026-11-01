from django.test import TransactionTestCase

from apps.shipments.infrastructure.persistence.django_unit_of_work import DjangoUnitOfWork
from apps.shipments.infrastructure.persistence.repositories.shipment_repository import (
    DjangoShipmentRepository,
)
from apps.shipments.models import ShipmentModel
from apps.shipments.tests.helpers import make_shipment


class ShipmentPersistenceTests(TransactionTestCase):
    def setUp(self):
        self.repository = DjangoShipmentRepository()

    def test_commit_and_round_trip_preserve_snapshots(self):
        shipment = make_shipment()
        with DjangoUnitOfWork():
            self.repository.save(shipment)
        self.assertEqual(self.repository.get_by_id(shipment.id), shipment)
        self.assertEqual(ShipmentModel.objects.count(), 1)

    def test_exception_rolls_back_insert(self):
        shipment = make_shipment()
        with self.assertRaises(RuntimeError):
            with DjangoUnitOfWork():
                self.repository.save(shipment)
                raise RuntimeError("Fallo después de insertar")
        self.assertFalse(ShipmentModel.objects.exists())

    def test_same_unit_of_work_can_be_reused_after_rollback(self):
        unit_of_work = DjangoUnitOfWork()
        with self.assertRaises(RuntimeError):
            with unit_of_work:
                self.repository.save(make_shipment())
                raise RuntimeError("Fallo temporal")
        with unit_of_work:
            self.repository.save(make_shipment())
        self.assertEqual(ShipmentModel.objects.count(), 1)
