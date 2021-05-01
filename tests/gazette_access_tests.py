import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
from datetime import date, timedelta

from gazettes import (
    GazetteAccess,
    GazetteAccessInterface,
    GazetteRequest,
    GazetteDataGateway,
    Gazette,
    create_gazettes_interface,
)


@GazetteDataGateway.register
class DummyDataGateway:
    pass


class InvalidDataGateway:
    pass


class GazetteAccessInterfacesTest(TestCase):
    @unittest.expectedFailure
    def test_create_gazette_access_interface_object_should_fail(self):
        self.gazette_access = GazetteAccessInterface()

    @unittest.expectedFailure
    def test_create_gazette_data_gateway_interface_object_should_fail(self):
        self.gazette_access = GazetteDataGateway()

    def test_create_gazettes_interface_should_return_a_valid_interface_object(self):
        interface = create_gazettes_interface(DummyDataGateway())
        self.assertIsInstance(interface, GazetteAccessInterface)

    @unittest.expectedFailure
    def test_create_gazettes_interface_with_invalid_data_gateway_should_fail(self):
        interace = create_gazettes_interface(InvalidDataGateway())

    def test_GazetteRequest_should_territory_id_attribute(self):
        territory_id = "1234"
        since = date.today()
        until = date.today() - timedelta(days=1)
        keywords = ["cnpj", "bla", "foo", "bar"]
        offset = 10
        size = 100
        request = GazetteRequest(territory_id, since, until, keywords, offset, size)
        self.assertEqual(
            territory_id, request.territory_id, msg="Territory ID is invalid"
        )
        self.assertEqual(since, request.since, msg="'Since' date is invalid")
        self.assertEqual(until, request.until, msg="'Until' date is invalid")
        self.assertEqual(keywords, request.keywords, msg="Keywords are invalid")
        self.assertEqual(offset, request.offset, msg="Offset are invalid")
        self.assertEqual(size, request.size, msg="Invalid number of items")


class GazetteAccessTest(TestCase):
    def setUp(self):
        self.return_value = [
            Gazette(
                "4205902",
                date.today(),
                "https://queridodiario.ok.org.br/",
                "so'jsdogjeogjsdogjheogdfsdf",
                "My city",
                "My state",
                "highlight"
                "123,456",
                False,
            ),
            Gazette(
                "4205902",
                (date.today() - timedelta(days=1)),
                "https://queridodiario.ok.org.br/",
                "a;oijaeofdjewofijrogho490jhfeasd",
                "My city",
                "My state",
                "highlight"
                "123,456",
                False,
            ),
            Gazette(
                "4205902",
                (date.today() + timedelta(days=1)),
                "https://queridodiario.ok.org.br/",
                "eolgpijdsfesuhrgfiuhsad",
                "My city",
                "My state",
                "highlight"
                "123,456",
                False,
            ),
            Gazette(
                "4202909",
                date.today(),
                "https://queridodiario.ok.org.br/",
                "ew;oigfdfsdjn;dajnorgf",
                "My city",
                "My state",
                "highlight"
                "123,456",
                False,
            ),
            Gazette(
                "4202909",
                (date.today() - timedelta(days=1)),
                "https://queridodiario.ok.org.br/",
                "sdosauiydhbfeicneqiudnewf",
                "My city",
                "My state",
                "highlight"
                "123,456",
                False,
            ),
            Gazette(
                "4202909",
                (date.today() + timedelta(days=1)),
                "https://queridodiario.ok.org.br/",
                "sdo;ifjwefonsdiasndiswabdisbfnidf",
                "My city",
                "My state",
                "highlight"
                "123,456",
                False,
            ),
        ]
        self.mock_data_gateway = MagicMock()
        self.mock_data_gateway.get_gazettes = MagicMock(
            return_value=(len(self.return_value), self.return_value)
        )
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
        items_count, gazettes = self.gazette_access.get_gazettes()
        self.assertEqual(items_count, len(self.return_value))
        self.assertEqual(len(self.return_value), len(gazettes))
        self.mock_data_gateway.get_gazettes.assert_called_once()

    def test_get_gazettes_should_return_dictionary(self):
        expected_results = [
            {
                "territory_id": gazette.territory_id,
                "date": gazette.date,
                "url": gazette.url,
                "checksum": gazette.checksum,
                "territory_name": gazette.territory_name,
                "state_code": gazette.state_code,
                "edition": gazette.edition,
                "is_extra_edition": gazette.is_extra_edition,
                "highlight_texts": gazette.highlight_texts,
            }
            for gazette in self.return_value
        ]

        _, gazettes = self.gazette_access.get_gazettes()
        self.assertCountEqual(expected_results, gazettes)

    def test_should_foward_filter_to_gateway(self):
        gazette_access = GazetteAccess(self.mock_data_gateway)
        list(
            self.gazette_access.get_gazettes(
                filters=GazetteRequest(territory_id="4205902")
            )[1]
        )
        self.mock_data_gateway.get_gazettes.assert_called_once_with(
            territory_id="4205902",
            since=None,
            until=None,
            keywords=None,
            offset=0,
            size=10,
            fragment_size=150,
            number_of_fragments=1,
            pre_tags=[''],
            post_tags=[''],
        )

    def test_should_foward_since_date_filter_to_gateway(self):
        gazette_access = GazetteAccess(self.mock_data_gateway)
        list(
            self.gazette_access.get_gazettes(
                filters=GazetteRequest(since=date.today())
            )[1]
        )
        self.mock_data_gateway.get_gazettes.assert_called_once_with(
            since=date.today(),
            until=None,
            territory_id=None,
            keywords=None,
            offset=0,
            size=10,
            fragment_size=150,
            number_of_fragments=1,
            pre_tags=[''],
            post_tags=[''],
        )

    def test_should_foward_until_date_filter_to_gateway(self):
        gazette_access = GazetteAccess(self.mock_data_gateway)
        list(
            self.gazette_access.get_gazettes(
                filters=GazetteRequest(until=date.today())
            )[1]
        )
        self.mock_data_gateway.get_gazettes.assert_called_once_with(
            until=date.today(),
            since=None,
            territory_id=None,
            keywords=None,
            offset=0,
            size=10,
            fragment_size=150,
            number_of_fragments=1,
            pre_tags=[''],
            post_tags=[''],
        )

    def test_should_foward_keywords_filter_to_gateway(self):
        gazette_access = GazetteAccess(self.mock_data_gateway)
        keywords = ["foo", "bar", "zpto"]
        list(
            self.gazette_access.get_gazettes(filters=GazetteRequest(keywords=keywords))[
                1
            ]
        )
        self.mock_data_gateway.get_gazettes.assert_called_once_with(
            until=None,
            since=None,
            territory_id=None,
            keywords=keywords,
            offset=0,
            size=10,
            fragment_size=150,
            number_of_fragments=1,
            pre_tags=[''],
            post_tags=[''],
        )

    def test_should_foward_page_fields_filter_to_gateway(self):
        gazette_access = GazetteAccess(self.mock_data_gateway)
        list(
            self.gazette_access.get_gazettes(
                filters=GazetteRequest(offset=10, size=100)
            )[1]
        )
        self.mock_data_gateway.get_gazettes.assert_called_once_with(
            until=None,
            since=None,
            territory_id=None,
            keywords=None,
            offset=10,
            size=100,
            fragment_size=150,
            number_of_fragments=1,
            pre_tags=[''],
            post_tags=[''],
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
        territory_name = "My city"
        state_code = "My state"
        highlight_texts = ["highlight"]
        edition = "123.45"
        is_extra_edition = False
        checksum = "qweolrjeglkjnasjdowejgorehn"
        gazette = Gazette(
            "ID",
            today,
            url,
            checksum,
            territory_name,
            state_code,
            highlight_texts,
            edition,
            is_extra_edition,
        )
        self.assertIsInstance(
            gazette.territory_id, str, msg="Territory ID should be string"
        )
        self.assertEqual("ID", gazette.territory_id)
        self.assertIsInstance(gazette.date, date, msg="Expected a date object")
        self.assertEqual(today, gazette.date)
        self.assertIsInstance(gazette.url, str, msg="URL should be a string")
        self.assertEqual(url, gazette.url)
        self.assertEqual(territory_name, gazette.territory_name)
        self.assertEqual(state_code, gazette.state_code)
        self.assertEqual(highlight_texts, gazette.highlight_texts)
        self.assertEqual(edition, gazette.edition)
        self.assertFalse(gazette.is_extra_edition)
        self.assertEqual(gazette.checksum, checksum)

    def test_gazette_without_edition_and_extra_fields(self):
        today = date.today()
        url = "https://queridodiario.ok.org.br/"
        checksum = "df;dsfnbkijdasjdasisdsad"
        territory_name = "My city"
        state_code = "My state"
        highlight_texts = ["highlight"]
        gazette = Gazette("ID", today, url, checksum, territory_name, state_code, highlight_texts)
        self.assertIsInstance(
            gazette.territory_id, str, msg="Territory ID should be string"
        )
        self.assertEqual("ID", gazette.territory_id)
        self.assertIsInstance(gazette.date, date, msg="Expected a date object")
        self.assertEqual(today, gazette.date)
        self.assertIsInstance(gazette.url, str, msg="URL should be a string")
        self.assertEqual(url, gazette.url)
        self.assertEqual(territory_name, gazette.territory_name)
        self.assertEqual(state_code, gazette.state_code)
        self.assertEqual(highlight_texts, gazette.highlight_texts)
        self.assertIsNone(gazette.edition)
        self.assertIsNone(gazette.is_extra_edition)
        self.assertEqual(gazette.checksum, checksum)
