from uuid import uuid4

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.branches.presentation.api.serializers import (
    BranchOutputSerializer,
    CreateBranchSerializer,
    UpdateBranchSerializer,
)
from apps.shipments.presentation.api.serializers import (
    CreateShipmentSerializer,
    ShipmentOutputSerializer,
)


class APIDocumentationTests(SimpleTestCase):
    def schema(self):
        response = self.client.get(reverse("openapi-schema"))
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_scalar_page_uses_local_schema_without_external_proxy(self):
        response = self.client.get(reverse("api-docs"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "api_docs.html")
        self.assertContains(response, reverse("openapi-schema"))
        self.assertContains(response, "@scalar/api-reference/esm.js")
        self.assertContains(response, "proxyUrl: ''")
        self.assertNotContains(response, "https://proxy.scalar.com")

    def test_documented_routes_and_methods_match_real_views(self):
        schema = self.schema()
        self.assertEqual(schema["openapi"], "3.0.3")
        self.assertEqual(schema["servers"], [{"url": "/", "description": "Servidor actual"}])
        identifier = uuid4()
        expected = {
            reverse("branch-list-create"),
            reverse("branch-update", kwargs={"branch_id": identifier}),
            reverse("shipment-create"),
            reverse("shipment-detail", kwargs={"shipment_id": identifier}),
        }
        documented = set()
        operation_ids = []
        for path, operations in schema["paths"].items():
            actual_path = path.format(branch_id=identifier, shipment_id=identifier)
            documented.add(actual_path)
            view = resolve(actual_path).func.view_class
            supported = {
                method for method in ("get", "post", "put", "patch", "delete")
                if hasattr(view, method)
            }
            self.assertEqual(set(operations), supported)
            for operation in operations.values():
                operation_ids.append(operation["operationId"])
                for parameter in operation.get("parameters", []):
                    self.assertTrue(parameter["required"])
                    self.assertEqual(parameter["schema"]["format"], "uuid")
        self.assertEqual(documented, expected)
        self.assertEqual(len(operation_ids), 7)
        self.assertEqual(len(set(operation_ids)), 7)

    def test_all_schema_references_resolve(self):
        schema = self.schema()

        def visit(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    reference = value["$ref"]
                    self.assertTrue(reference.startswith("#/"))
                    target = schema
                    for part in reference[2:].split("/"):
                        target = target[part.replace("~1", "/").replace("~0", "~")]
                    self.assertIsInstance(target, dict)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)

        visit(schema)

    def test_schema_fields_and_required_inputs_match_serializers(self):
        schemas = self.schema()["components"]["schemas"]
        cases = (
            ("CreateBranchRequest", CreateBranchSerializer()),
            ("UpdateBranchRequest", UpdateBranchSerializer()),
            ("PatchBranchRequest", UpdateBranchSerializer(partial=True)),
            ("Branch", BranchOutputSerializer()),
            ("CreateShipmentRequest", CreateShipmentSerializer()),
            ("Shipment", ShipmentOutputSerializer()),
        )
        for name, serializer in cases:
            with self.subTest(component=name):
                component = schemas[name]
                self.assertEqual(set(component["properties"]), set(serializer.fields))
                expected_required = {
                    name for name, field in serializer.fields.items()
                    if field.required and not serializer.partial
                }
                self.assertEqual(set(component.get("required", [])), expected_required)
        self.assertEqual(schemas["PatchBranchRequest"]["minProperties"], 1)
        self.assertFalse(schemas["PatchBranchRequest"]["additionalProperties"])
        self.assertTrue(schemas["CreateBranchRequest"]["properties"]["is_active"]["default"])

    def test_creation_and_lists_have_correct_response_shapes(self):
        schema = self.schema()
        for path, component in (("/api/branches/", "Branch"), ("/api/shipments/", "Shipment")):
            with self.subTest(path=path):
                creation = schema["paths"][path]["post"]
                self.assertIn("201", creation["responses"])
                self.assertTrue(creation["requestBody"]["required"])
                listing = schema["paths"][path]["get"]
                result = listing["responses"]["200"]["content"]["application/json"]["schema"]
                self.assertEqual(result, {
                    "type": "array", "items": {"$ref": f"#/components/schemas/{component}"}
                })
        self.assertEqual(set(schema["components"]["responses"]), {
            "Error400", "Error404", "Error409", "Error422", "Error503"
        })
        self.assertEqual(schema["components"]["schemas"]["Error"]["required"], ["code", "detail"])

    def test_documentation_endpoints_are_read_only(self):
        for name in ("api-docs", "openapi-schema"):
            with self.subTest(name=name):
                self.assertEqual(self.client.head(reverse(name)).status_code, 200)
                self.assertEqual(self.client.post(reverse(name)).status_code, 405)
