from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from apps.shipments.application.exceptions import CountryCatalogUnavailableError
from apps.shipments.infrastructure.integrations.countries_api.country_catalog import (
    GraphQLCountryCatalog,
)
from apps.shipments.infrastructure.integrations.countries_api.graphql_client import (
    CountryGraphQLClient,
)
from apps.shipments.infrastructure.integrations.countries_api.mappers.country_mapper import (
    CountryGraphQLMapper,
)


POST_PATH = (
    "apps.shipments.infrastructure.integrations.countries_api.graphql_client.requests.post"
)


class CountryCatalogTests(SimpleTestCase):
    def setUp(self):
        client = CountryGraphQLClient("https://example.invalid/graphql", (3, 5))
        self.catalog = GraphQLCountryCatalog(client, CountryGraphQLMapper())

    def response(self, payload):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = payload
        return response

    def test_valid_country_is_mapped_and_query_uses_variables(self):
        payload = {"data": {"country": {"code": "CR", "name": "Costa Rica", "currency": "CRC"}}}
        with patch(POST_PATH, return_value=self.response(payload)) as post:
            result = self.catalog.get_country("CR")
        self.assertEqual(result.code, "CR")
        self.assertEqual(result.currency, "CRC")
        self.assertEqual(post.call_args.kwargs["json"]["variables"], {"code": "CR"})
        self.assertEqual(post.call_args.kwargs["timeout"], (3, 5))

    def test_null_country_means_not_found(self):
        with patch(POST_PATH, return_value=self.response({"data": {"country": None}})):
            self.assertIsNone(self.catalog.get_country("XX"))

    def test_bad_or_partial_responses_are_not_reported_as_missing(self):
        payloads = [
            [],
            {"errors": [{"message": "Fallo"}], "data": {"country": None}},
            {"data": None},
            {"data": {}},
            {"data": {"country": {"code": "CR", "name": "Costa Rica", "currency": None}}},
            {"data": {"country": {"code": "NI", "name": "Nicaragua", "currency": "NIO"}}},
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                with patch(POST_PATH, return_value=self.response(payload)):
                    with self.assertRaises(CountryCatalogUnavailableError):
                        self.catalog.get_country("CR")

    def test_timeout_is_translated(self):
        with patch(POST_PATH, side_effect=requests.Timeout("timeout")):
            with self.assertRaises(CountryCatalogUnavailableError):
                self.catalog.get_country("CR")

    def test_http_error_is_translated(self):
        response = self.response({})
        response.raise_for_status.side_effect = requests.HTTPError("503")
        with patch(POST_PATH, return_value=response):
            with self.assertRaises(CountryCatalogUnavailableError):
                self.catalog.get_country("CR")

    def test_invalid_json_is_translated(self):
        response = self.response({})
        response.json.side_effect = ValueError("JSON inválido")
        with patch(POST_PATH, return_value=response):
            with self.assertRaises(CountryCatalogUnavailableError):
                self.catalog.get_country("CR")
