from unittest import TestCase
from unittest.mock import MagicMock

from gazettes import GazetteAccess, GazetteRequest, GazetteDataGateway, Gazette


class GazetteAccessTest(TestCase):
    def setUp(self):
        self.mock_data_gateway = GazetteDataGateway()
        self.mock_data_gateway.get_gazettes = MagicMock(
            return_value=[Gazette("4205902"), Gazette("4202909")]
        )
        self.gazette_access = GazetteAccess(self.mock_data_gateway)

    def test_create_gazette_access(self):
        self.assertIsNotNone(
            self.gazette_access, msg="Could not create GazetteAccess object"
        )

    def test_get_gazettes(self):
        self.assertEqual(2, len(list(self.gazette_access.get_gazettes())))
        self.mock_data_gateway.get_gazettes.assert_called_once()

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


class GazetteDataGatewayInterfaceTest(TestCase):
    def test_create_gazette_access(self):
        gateway = GazetteDataGateway()
        with self.assertRaises(Exception):
            gateway.get_gazettes()


class GazetteRequestTest(TestCase):
    def test_gazette_request_creation(self):
        gazette_request = GazetteRequest("ID")
        self.assertIsInstance(gazette_request.territory_id, str)
        self.assertEqual("ID", gazette_request.territory_id)


class GazetteTest(TestCase):
    def test_gazette_creation(self):
        gazette = Gazette("ID")
        self.assertIsInstance(gazette.territory_id, str)
        self.assertEqual("ID", gazette.territory_id)
