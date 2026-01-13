from datetime import date, timedelta, datetime
from unittest.mock import MagicMock
from unittest import TestCase, expectedFailure

from fastapi.testclient import TestClient

from api import app, configure_api_app
from gazettes import GazetteAccessInterface, GazetteRequest
from suggestions import Suggestion, SuggestionSent, SuggestionServiceInterface
from companies import CompaniesAccessInterface
from themed_excerpts import ThemedExcerptAccessInterface
from cities import CityAccessInterface
from aggregates import AggregatesAccessInterface

from tests.test_helpers import (
    create_default_mocks,
    create_mock_gazette_interface,
    MockSuggestionService,
)


class ApiGazettesEndpointTests(TestCase):
    def test_api_should_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        with self.assertRaises(Exception):
            configure_api_app(MagicMock(), *create_default_mocks()[1:])

    def test_api_should_not_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        configure_api_app(*create_default_mocks())

    def test_gazettes_endpoint_should_accept_territory_ids_as_query_param(self):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"territory_ids": ["4205902"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ["4205902"], interface.get_gazettes.call_args.args[0].territory_ids
        )
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_until)
        self.assertEqual("", interface.get_gazettes.call_args.args[0].querystring)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].offset)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].size)

    def test_gazettes_endpoint_should_accept_query_published_since_date(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={
                "territory_ids": ["4205902"],
                "published_since": date.today().strftime("%Y-%m-%d"),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_published_until_date(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={
                "territory_ids": ["4205902"],
                "published_until": date.today().strftime("%Y-%m-%d"),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_fail_with_invalid_published_since_value(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={"territory_ids": ["4205902"], "published_since": "foo-bar-2222"},
        )
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_published_until_value(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={"territory_ids": ["4205902"], "published_until": "foo-bar-2222"},
        )
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_pagination_data(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={"territory_ids": ["4205902"], "offset": "asfasdasd", "size": "10"},
        )
        self.assertEqual(response.status_code, 422)
        response = client.get(
            "/gazettes",
            params={"territory_ids": ["4205902"], "offset": "10", "size": "ssddsfds"},
        )
        self.assertEqual(response.status_code, 422)
        response = client.get(
            "/gazettes",
            params={"territory_ids": ["4205902"], "offset": "x", "size": "asdasdas"},
        )
        self.assertEqual(response.status_code, 422)

    def test_get_gazettes_without_territory_ids_should_be_fine(self):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([], interface.get_gazettes.call_args.args[0].territory_ids)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_until)
        self.assertEqual("", interface.get_gazettes.call_args.args[0].querystring)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].offset)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].size)

    def test_get_gazettes_should_request_gazettes_to_interface_object(self):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"territory_ids": ["4205902"]})
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()

    def test_get_gazettes_should_forward_gazettes_filters_to_interface_object(self):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={
                "territory_ids": ["4205902"],
                "published_since": date.today().strftime("%Y-%m-%d"),
                "published_until": date.today().strftime("%Y-%m-%d"),
                "offset": 10,
                "size": 100,
            },
        )
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids, ["4205902"]
        )
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].published_since,
            date.today(),
        )
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].published_until, date.today()
        )
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 10)
        self.assertEqual(interface.get_gazettes.call_args.args[0].size, 100)

    def test_get_gazettes_should_return_json_with_items(self):
        today = date.today()
        scraped_at = datetime.now()
        interface = create_mock_gazette_interface(
            (
                1,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "scraped_at": scraped_at,
                        "txt_url": None,
                        "excerpts": ["test"],
                    }
                ],
            )
        )
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"territory_ids": ["4205902"]})
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids, ["4205902"]
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["total_gazettes"], 1)
        self.assertEqual(len(response_data["gazettes"]), 1)
        gazette = response_data["gazettes"][0]
        self.assertEqual(gazette["territory_id"], "4205902")
        self.assertEqual(gazette["date"], today.strftime("%Y-%m-%d"))
        self.assertEqual(gazette["url"], "https://queridodiario.ok.org.br/")
        self.assertEqual(gazette["territory_name"], "My city")
        self.assertEqual(gazette["state_code"], "My state")
        self.assertEqual(gazette["is_extra_edition"], False)
        self.assertEqual(gazette["edition"], "12.3442")
        self.assertEqual(gazette["excerpts"], ["test"])
        self.assertIn("scraped_at", gazette)

    def test_get_gazettes_should_return_empty_list_when_no_gazettes_is_found(self):
        today = date.today()
        scraped_at = datetime.now()
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"territory_ids": ["4205902"]})
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids, ["4205902"]
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"total_gazettes": 0, "gazettes": []},
        )

    def test_gazettes_endpoint_should_accept_query_querystring_date(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={"territory_ids": "4205902", "querystring": "keyword1 keyword2"},
        )
        self.assertEqual(response.status_code, 200)
        response = client.get(
            "/gazettes", params={"territory_ids": "4205902", "querystring": []}
        )
        self.assertEqual(response.status_code, 200)

    def test_get_gazettes_should_forward_querystring_to_interface_object(self):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)

        response = client.get(
            "/gazettes",
            params={"territory_ids": "4205902", "querystring": "keyword1 1 True"},
        )
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].querystring, "keyword1 1 True"
        )

        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        response = client.get(
            "/gazettes", params={"territory_ids": "4205902", "querystring": None}
        )
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].querystring, "")

        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        response = client.get(
            "/gazettes", params={"territory_ids": "4205902", "querystring": ""}
        )
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].querystring, "")

    def test_gazettes_without_territory_endpoint__should_accept_query_since_date(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes", params={"since": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_endpoint__should_accept_query_until_date(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes", params={"until": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_endpoint__should_fail_with_invalid_since_value(
        self,
    ):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"published_since": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_gazettes_without_territory_endpoint__should_fail_with_invalid_until_value(
        self,
    ):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"published_until": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_get_gazettes_without_territory_ids_should_forward_gazettes_filters_to_interface_object(
        self,
    ):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={
                "published_since": date.today().strftime("%Y-%m-%d"),
                "published_until": date.today().strftime("%Y-%m-%d"),
                "offset": 10,
                "size": 100,
            },
        )
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual([], interface.get_gazettes.call_args.args[0].territory_ids)
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].published_since,
            date.today(),
        )
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].published_until, date.today()
        )
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 10)
        self.assertEqual(interface.get_gazettes.call_args.args[0].size, 100)

    def test_api_should_forward_the_result_offset(self):
        interface = create_mock_gazette_interface()
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={
                "offset": 0,
            },
        )
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 0)

    @expectedFailure
    def test_configure_api_should_failed_with_invalid_root_path(self):
        configure_api_app(
            *create_default_mocks(),
            api_root_path=1,
        )

    def test_configure_api_root_path(self):
        configure_api_app(
            *create_default_mocks(),
            api_root_path="/api/v1",
        )
        self.assertEqual("/api/v1", app.root_path)

    def test_api_without_edition_and_extra_field(self):
        today = date.today()
        scraped_at = datetime.now()
        yesterday = today - timedelta(days=1)
        interface = create_mock_gazette_interface(
            (
                2,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "scraped_at": scraped_at,
                        "txt_url": None,
                        "excerpts": ["test"],
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "scraped_at": scraped_at,
                        "txt_url": None,
                        "excerpts": ["test"],
                        "edition": None,
                        "is_extra_edition": None,
                    },
                ],
            )
        )
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"territory_ids": ["4205902"]})
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids, ["4205902"]
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["total_gazettes"], 2)
        self.assertEqual(len(response_data["gazettes"]), 2)

        # Verificar primeira gazette
        gazette1 = response_data["gazettes"][0]
        self.assertEqual(gazette1["territory_id"], "4205902")
        self.assertEqual(gazette1["date"], today.strftime("%Y-%m-%d"))
        self.assertEqual(gazette1["edition"], "12.3442")
        self.assertIn("scraped_at", gazette1)
        self.assertIn("excerpts", gazette1)

        # Verificar segunda gazette
        gazette2 = response_data["gazettes"][1]
        self.assertEqual(gazette2["territory_id"], "4205902")
        self.assertEqual(gazette2["date"], yesterday.strftime("%Y-%m-%d"))
        self.assertIn("scraped_at", gazette2)
        self.assertIn("excerpts", gazette2)

    def test_api_with_none_edition_and_extra_field(self):
        today = date.today()
        scraped_at = datetime.now()
        yesterday = today - timedelta(days=1)
        interface = create_mock_gazette_interface(
            (
                2,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "scraped_at": scraped_at,
                        "txt_url": None,
                        "excerpts": ["test"],
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": None,
                        "edition": None,
                        "scraped_at": scraped_at,
                        "txt_url": None,
                        "excerpts": ["test"],
                    },
                ],
            )
        )
        configure_api_app(interface, *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/gazettes", params={"territory_ids": ["4205902"]})
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids, ["4205902"]
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["total_gazettes"], 2)
        self.assertEqual(len(response_data["gazettes"]), 2)

        # Verificar que campos obrigatórios existem em ambas as gazettes
        for gazette in response_data["gazettes"]:
            self.assertIn("territory_id", gazette)
            self.assertIn("date", gazette)
            self.assertIn("scraped_at", gazette)
            self.assertIn("excerpts", gazette)
            self.assertIn("url", gazette)

    def test_cities_endpoint_should_accept_request_without_partial_city_name(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)

    def test_cities_should_return_some_city_info(self):
        configure_api_app(create_mock_gazette_interface(), *create_default_mocks()[1:])
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"cities": []},
        )

    def test_cities_should_request_data_from_city_interface(self):
        mocks = create_default_mocks()
        city_mock = mocks[2]  # CityAccessInterface
        configure_api_app(*mocks)
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        city_mock.get_cities.assert_called_once()

    def test_cities_should_return_data_returned_by_city_interface(self):
        mocks = create_default_mocks()
        city_mock = mocks[2]
        city_mock.get_cities.return_value = [
            {
                "territory_id": "1234",
                "territory_name": "piraporia",
                "state_code": "SC",
                "publication_urls": ["https://querido-diario.org.br"],
                "level": "1",
                "availability_date": "2020-01-01",
            }
        ]
        configure_api_app(*mocks)
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "cities": [
                    {
                        "territory_id": "1234",
                        "territory_name": "piraporia",
                        "state_code": "SC",
                        "publication_urls": ["https://querido-diario.org.br"],
                        "level": "1",
                        "availability_date": "2020-01-01",
                    }
                ]
            },
        )

    def test_city_endpoint_should_accept_request_with_city_id(self):
        mocks = create_default_mocks()
        city_mock = mocks[2]
        city_mock.get_city.return_value = {
            "territory_id": "1234",
            "territory_name": "piraporia",
            "state_code": "SC",
            "publication_urls": ["https://querido-diario.org.br"],
            "level": "1",
            "availability_date": "2020-01-01",
        }
        configure_api_app(*mocks)
        client = TestClient(app)
        response = client.get("/cities/1234")
        self.assertEqual(response.status_code, 200)

    def test_city_endpoint_should_return_404_with_city_id_not_found(self):
        mocks = create_default_mocks()
        city_mock = mocks[2]
        city_mock.get_city.return_value = None
        configure_api_app(*mocks)
        client = TestClient(app)
        response = client.get("/cities/1234")
        self.assertEqual(response.status_code, 404)

    def test_city_endpoint_should_request_data_from_city_interface(self):
        mocks = create_default_mocks()
        city_mock = mocks[2]
        city_mock.get_city.return_value = {
            "territory_id": "1234",
            "territory_name": "piraporia",
            "state_code": "SC",
            "publication_urls": ["https://querido-diario.org.br"],
            "level": "1",
            "availability_date": "2020-01-01",
        }
        configure_api_app(*mocks)
        client = TestClient(app)
        response = client.get("/cities/1234")
        city_mock.get_city.assert_called_once()

    def test_city_endpoint_should_return_city_info_returned_by_city_interface(self):
        mocks = create_default_mocks()
        city_mock = mocks[2]
        city_mock.get_city.return_value = {
            "territory_id": "1234",
            "territory_name": "piraporia",
            "state_code": "SC",
            "publication_urls": ["https://querido-diario.org.br"],
            "level": "1",
            "availability_date": "2020-01-01",
        }
        configure_api_app(*mocks)
        client = TestClient(app)
        response = client.get("/cities/1234")
        self.assertEqual(
            response.json(),
            {
                "city": {
                    "territory_id": "1234",
                    "territory_name": "piraporia",
                    "state_code": "SC",
                    "publication_urls": ["https://querido-diario.org.br"],
                    "level": "1",
                    "availability_date": "2020-01-01",
                }
            },
        )


class ApiSuggestionsEndpointTests(TestCase):
    def setUp(self):
        self.suggestion_service = MockSuggestionService()
        mocks = create_default_mocks()
        # Substituir suggestion_service pelo nosso mock customizado
        configure_api_app(
            mocks[0],  # gazettes
            mocks[1],  # themed_excerpts
            mocks[2],  # cities
            self.suggestion_service,  # suggestion_service customizado
            mocks[4],  # companies
            mocks[5],  # aggregates
        )
        self.client = TestClient(app)

    def test_suggestion_endpoint_should_send_email(self):
        suggestion_sent = SuggestionSent(success=True, status="sent")
        self.suggestion_service.add_suggestion = MagicMock(return_value=suggestion_sent)

        response = self.client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "name": "My Name",
                "content": "Suggestion content",
            },
        )
        assert response.status_code == 200
        assert response.json() == {"status": "sent"}

    def test_api_should_fail_when_try_to_set_any_object_as_suggestions_service_interface(
        self,
    ):
        with self.assertRaises(Exception):
            configure_api_app(
                MockGazetteAccessInterface(),
                MagicMock(),
            )

    def test_suggestion_endpoint_should_fail_send_email(self):
        suggestion_sent = SuggestionSent(
            success=False, status="Could not sent message: an error"
        )
        self.suggestion_service.add_suggestion = MagicMock(return_value=suggestion_sent)

        response = self.client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "name": "My Name",
                "content": "Suggestion content",
            },
        )
        assert response.status_code == 400
        assert response.json() == {"status": "Could not sent message: an error"}

    def test_suggestion_endpoint_should_reject_when_email_address_is_not_present(self):
        response = self.client.post(
            "/suggestions",
            json={
                "name": "My Name",
                "content": "Suggestion content",
            },
        )
        assert response.status_code == 422
        response_data = response.json()
        assert len(response_data["detail"]) == 1
        error = response_data["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "email_address"]
        assert error["msg"] == "Field required"

    def test_suggestion_endpoint_should_reject_when_name_is_not_present(self):
        response = self.client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "content": "Suggestion content",
            },
        )
        assert response.status_code == 422
        response_data = response.json()
        assert len(response_data["detail"]) == 1
        error = response_data["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "name"]
        assert error["msg"] == "Field required"

    def test_suggestion_endpoint_should_reject_when_content_is_not_present(self):
        response = self.client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "name": "My Name",
            },
        )
        assert response.status_code == 422
        response_data = response.json()
        assert len(response_data["detail"]) == 1
        error = response_data["detail"][0]
        assert error["type"] == "missing"
        assert error["loc"] == ["body", "content"]
        assert error["msg"] == "Field required"
