from datetime import date
from unittest.mock import MagicMock
from unittest import TestCase

from fastapi.testclient import TestClient

from api import app, set_gazette_interface
from gazettes import GazetteAccessInterface, GazetteRequest


@GazetteAccessInterface.register
class MockGazetteAccessInterface:
    pass


class ApiTests(TestCase):
    def create_mock_gazette_interface(self, return_value=None):
        interface = MockGazetteAccessInterface()
        interface.get_gazettes = MagicMock(return_value=return_value)
        return interface

    def test_api_should_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        with self.assertRaises(Exception):
            set_gazette_interface(MagicMock())

    def test_api_should_not_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        set_gazette_interface(MockGazetteAccessInterface())

    def test_gazettes_endpoint_should_accept_territory_id(self):
        set_gazette_interface(self.create_mock_gazette_interface())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_since_date(self):
        set_gazette_interface(self.create_mock_gazette_interface())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902", params={"since": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_until_date(self):
        set_gazette_interface(self.create_mock_gazette_interface())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902", params={"until": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_fail_with_invalid_since_value(self):
        set_gazette_interface(self.create_mock_gazette_interface())
        client = TestClient(app)
        response = client.get("/gazettes/4205902", params={"since": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_until_value(self):
        set_gazette_interface(self.create_mock_gazette_interface())
        client = TestClient(app)
        response = client.get("/gazettes/4205902", params={"until": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_get_gazettes_without_territory_id_should_fail(self):
        set_gazette_interface(MockGazetteAccessInterface())
        client = TestClient(app)
        response = client.get("/gazettes/")
        self.assertEqual(response.status_code, 404)

    def test_get_gazettes_should_request_gazettes_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        set_gazette_interface(interface)
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()

    def test_get_gazettes_should_forward_gazettes_filters_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        set_gazette_interface(interface)
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902",
            params={
                "since": date.today().strftime("%Y-%m-%d"),
                "until": date.today().strftime("%Y-%m-%d"),
            },
        )
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].since, date.today(),
        )
        self.assertEqual(interface.get_gazettes.call_args.args[0].until, date.today())

    def test_get_gazettes_should_return_json_with_items(self):
        today = date.today()
        interface = self.create_mock_gazette_interface(
            [
                {
                    "territory_id": "4205902",
                    "date": today,
                    "url": "https://queridodiario.ok.org.br/",
                }
            ]
        )
        set_gazette_interface(interface)
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "territory_id": "4205902",
                    "date": today.strftime("%Y-%m-%d"),
                    "url": "https://queridodiario.ok.org.br/",
                }
            ],
        )

    def test_get_gazettes_should_return_empty_list_when_no_gazettes_is_found(self):
        today = date.today()
        interface = self.create_mock_gazette_interface()
        set_gazette_interface(interface)
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
