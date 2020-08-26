from unittest import TestCase
from unittest.mock import MagicMock
from datetime import date

from gazettes import (
    GazetteAccess,
    GazetteAccessInterface,
    GazetteRequest,
    GazetteDataGateway,
    Gazette,
)


class GazetteAccessInterfacesTest(TestCase):
    def test_create_gazette_access_interface_object_should_fail(self):
        with self.assertRaises(Exception):
            self.gazette_access = GazetteAccessInterface()

    def test_create_gazette_data_gateway_interface_object_should_fail(self):
        with self.assertRaises(Exception):
            self.gazette_access = GazetteDataGateway()


class GazetteAccessTest(TestCase):
    def setUp(self):
        self.return_value = [
            Gazette("4205902", date.today(), "https://queridodiario.ok.org.br/"),
            Gazette("4202909", date.today(), "https://queridodiario.ok.org.br/"),
        ]
        self.mock_data_gateway = MagicMock()
        self.mock_data_gateway.get_gazettes = MagicMock(return_value=self.return_value)
        self.gazette_access = GazetteAccess(self.mock_data_gateway)

    def test_create_gazette_access(self):
        self.assertIsNotNone(
            self.gazette_access, msg="Could not create GazetteAccess object"
        )
        self.assertIsInstance(
            self.gazette_access,
            GazetteAccessInterface,
            msg="The GazetteAccess object should implement GazetteAccessInterface",
        )

    def test_get_gazettes(self):
        self.assertEqual(2, len(list(self.gazette_access.get_gazettes())))
        self.mock_data_gateway.get_gazettes.assert_called_once()

    def test_get_gazettes_should_return_dictionary(self):
        expected_results = [
            {
                "territory_id": "4205902",
                "date": date.today(),
                "url": "https://queridodiario.ok.org.br/",
            },
            {
                "territory_id": "4202909",
                "date": date.today(),
                "url": "https://queridodiario.ok.org.br/",
            },
        ]

        gazettes = self.gazette_access.get_gazettes()
        self.assertCountEqual(expected_results, gazettes)

    def test_should_foward_filter_to_gateway(self):
        gazette_access = GazetteAccess(self.mock_data_gateway)
        list(
            self.gazette_access.get_gazettes(
                filters=GazetteRequest(territory_id="4205902")
            )
        )
        self.mock_data_gateway.get_gazettes.assert_called_once_with(
            territory_id="4205902"
        )


class GazetteRequestTest(TestCase):
    def test_gazette_request_creation(self):
        gazette_request = GazetteRequest("ID")
        self.assertIsInstance(gazette_request.territory_id, str)
        self.assertEqual("ID", gazette_request.territory_id)


class GazetteTest(TestCase):
    def test_gazette_creation(self):
        today = date.today()
        url = "https://queridodiario.ok.org.br/"
        gazette = Gazette("ID", today, url)
        self.assertIsInstance(
            gazette.territory_id, str, msg="Territory ID should be string"
        )
        self.assertEqual("ID", gazette.territory_id)
        self.assertIsInstance(gazette.date, date, msg="Expected a date object")
        self.assertEqual(today, gazette.date)
        self.assertIsInstance(gazette.url, str, msg="URL should be a string")
        self.assertEqual(url, gazette.url)
