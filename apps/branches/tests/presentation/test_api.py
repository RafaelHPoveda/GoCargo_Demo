from rest_framework.test import APITestCase
from uuid import uuid4

from apps.branches.models import BranchModel


class BranchAPITests(APITestCase):
    def setUp(self):
        self.payload = {
            "name": "Managua",
            "city": "Managua",
            "max_weight_kg": "25.00",
            "is_active": True,
        }

    def test_create_and_list(self):
        response = self.client.post("/api/branches/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BranchModel.objects.count(), 1)
        listing = self.client.get("/api/branches/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data[0]["id"], response.data["id"])

    def test_invalid_capacity_is_rejected_without_writing(self):
        self.payload["max_weight_kg"] = "0.00"
        response = self.client.post("/api/branches/", self.payload, format="json")
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.data["code"], "invalid_branch")
        self.assertFalse(BranchModel.objects.exists())

    def test_missing_field_returns_400(self):
        del self.payload["city"]
        response = self.client.post("/api/branches/", self.payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "invalid_request")

    def create_branch(self):
        response = self.client.post("/api/branches/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        return response.data["id"]

    def test_put_updates_all_fields_without_creating_another_branch(self):
        branch_id = self.create_branch()
        updated = {
            "name": "Sucursal Leon",
            "city": "Leon",
            "max_weight_kg": "10.50",
            "is_active": False,
        }
        response = self.client.put(f"/api/branches/{branch_id}/", updated, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], branch_id)
        self.assertEqual(response.data["city"], "Leon")
        branch = BranchModel.objects.get(pk=branch_id)
        self.assertFalse(branch.is_active)
        self.assertEqual(str(branch.max_weight_kg), "10.50")
        self.assertEqual(BranchModel.objects.count(), 1)

    def test_patch_preserves_omitted_fields_and_accepts_false(self):
        branch_id = self.create_branch()
        response = self.client.patch(
            f"/api/branches/{branch_id}/", {"is_active": False}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        branch = BranchModel.objects.get(pk=branch_id)
        self.assertFalse(branch.is_active)
        self.assertEqual(branch.name, self.payload["name"])
        self.assertEqual(str(branch.max_weight_kg), "25.00")

    def test_put_requires_all_mutable_fields(self):
        branch_id = self.create_branch()
        response = self.client.put(
            f"/api/branches/{branch_id}/", {"name": "Otro"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(BranchModel.objects.get(pk=branch_id).name, "Managua")

    def test_update_missing_branch_returns_404_without_inserting(self):
        response = self.client.patch(
            f"/api/branches/{uuid4()}/", {"name": "Otro"}, format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "branch_not_found")
        self.assertFalse(BranchModel.objects.exists())

    def test_invalid_capacity_leaves_previous_data_unchanged(self):
        branch_id = self.create_branch()
        response = self.client.patch(
            f"/api/branches/{branch_id}/",
            {"name": "No debe guardarse", "max_weight_kg": "0.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 422)
        branch = BranchModel.objects.get(pk=branch_id)
        self.assertEqual(branch.name, "Managua")
        self.assertEqual(str(branch.max_weight_kg), "25.00")

    def test_null_empty_or_immutable_fields_are_rejected(self):
        branch_id = self.create_branch()
        for payload in ({}, {"name": None}, {"id": str(uuid4())}, {"name": "   "}):
            with self.subTest(payload=payload):
                response = self.client.patch(
                    f"/api/branches/{branch_id}/", payload, format="json"
                )
                self.assertEqual(response.status_code, 400)
        self.assertEqual(BranchModel.objects.get(pk=branch_id).name, "Managua")
