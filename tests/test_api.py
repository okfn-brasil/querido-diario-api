from datetime import date, timedelta
from unittest.mock import MagicMock
from unittest import TestCase, expectedFailure

from fastapi.testclient import TestClient

from api import app, configure_api_app
from gazettes import GazetteAccessInterface, GazetteRequest
from suggestions import Suggestion, SuggestionSent, SuggestionServiceInterface


@GazetteAccessInterface.register
class MockGazetteAccessInterface:
    pass


@SuggestionServiceInterface.register
class MockSuggestionService:
    pass


class ApiGazettesEndpointTests(TestCase):
    def create_mock_gazette_interface(
        self, return_value=(0, []), cities_info=[], city_info=None
    ):
        interface = MockGazetteAccessInterface()
        interface.get_gazettes = MagicMock(return_value=return_value)
        interface.get_cities = MagicMock(return_value=cities_info)
        interface.get_city = MagicMock(return_value=city_info)
        return interface

    def test_api_should_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        with self.assertRaises(Exception):
            configure_api_app(MagicMock(), MockSuggestionService())

    def test_api_should_not_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        configure_api_app(MockGazetteAccessInterface(), MockSuggestionService())

    def test_gazettes_endpoint_should_accept_territory_id_in_the_path(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            "4205902", interface.get_gazettes.call_args.args[0].territory_id
        )
        self.assertIsNone(interface.get_gazettes.call_args.args[0].since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].until)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].querystring)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].offset)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].size)

    def test_gazettes_endpoint_should_accept_query_since_date(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902", params={"since": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_until_date(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902", params={"until": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_fail_with_invalid_since_value(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902", params={"since": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_until_value(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902", params={"until": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_pagination_data(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902", params={"offset": "asfasdasd", "size": "10"}
        )
        self.assertEqual(response.status_code, 422)
        response = client.get(
            "/gazettes/4205902", params={"offset": "10", "size": "ssddsfds"}
        )
        self.assertEqual(response.status_code, 422)
        response = client.get(
            "/gazettes/4205902", params={"offset": "x", "size": "asdasdas"}
        )
        self.assertEqual(response.status_code, 422)

    def test_get_gazettes_without_territory_id_should_be_fine(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].territory_id)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].until)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].querystring)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].offset)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].size)

    def test_get_gazettes_should_request_gazettes_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()

    def test_get_gazettes_should_forward_gazettes_filters_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902",
            params={
                "since": date.today().strftime("%Y-%m-%d"),
                "until": date.today().strftime("%Y-%m-%d"),
                "offset": 10,
                "size": 100,
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
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 10)
        self.assertEqual(interface.get_gazettes.call_args.args[0].size, 100)

    def test_get_gazettes_should_return_json_with_items(self):
        today = date.today()
        interface = self.create_mock_gazette_interface(
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
                        "highlight_texts": ["test"],
                    }
                ],
            )
        )
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_gazettes": 1,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today.strftime("%Y-%m-%d"),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "highlight_texts": ["test"],
                    }
                ],
            },
        )

    def test_get_gazettes_should_return_empty_list_when_no_gazettes_is_found(self):
        today = date.today()
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"total_gazettes": 0, "gazettes": []},
        )

    def test_gazettes_endpoint_should_accept_query_querystring_date(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes/4205902", params={"querystring": "keyword1 keyword2"}
        )
        self.assertEqual(response.status_code, 200)
        response = client.get("/gazettes/4205902", params={"querystring": []})
        self.assertEqual(response.status_code, 200)

    def test_get_gazettes_should_forward_querystring_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)

        response = client.get(
            "/gazettes/4205902", params={"querystring": "keyword1 1 True"}
        )
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].querystring, "keyword1 1 True"
        )

        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        response = client.get("/gazettes/4205902", params={"querystring": None})
        interface.get_gazettes.assert_called_once()
        self.assertIsNone(interface.get_gazettes.call_args.args[0].querystring)

        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        response = client.get("/gazettes/4205902", params={"querystring": ""})
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].querystring, "")

    def test_gazettes_without_territory_endpoint__should_accept_query_since_date(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes", params={"since": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_endpoint__should_accept_query_until_date(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes", params={"until": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_endpoint__should_fail_with_invalid_since_value(
        self,
    ):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes", params={"since": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_gazettes_without_territory_endpoint__should_fail_with_invalid_until_value(
        self,
    ):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes", params={"until": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_get_gazettes_without_territory_id_should_forward_gazettes_filters_to_interface_object(
        self,
    ):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get(
            "/gazettes",
            params={
                "since": date.today().strftime("%Y-%m-%d"),
                "until": date.today().strftime("%Y-%m-%d"),
                "offset": 10,
                "size": 100,
            },
        )
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertIsNone(interface.get_gazettes.call_args.args[0].territory_id)
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].since, date.today(),
        )
        self.assertEqual(interface.get_gazettes.call_args.args[0].until, date.today())
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 10)
        self.assertEqual(interface.get_gazettes.call_args.args[0].size, 100)

    def test_api_should_forward_the_result_offset(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes", params={"offset": 0,},)
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 0)

    @expectedFailure
    def test_configure_api_should_failed_with_invalid_root_path(self):
        configure_api_app(
            MockGazetteAccessInterface(), MockSuggestionService(), api_root_path=1
        )

    def test_configure_api_root_path(self):
        configure_api_app(
            MockGazetteAccessInterface(),
            MockSuggestionService(),
            api_root_path="/api/v1",
        )
        self.assertEqual("/api/v1", app.root_path)

    def test_api_without_edition_and_extra_field(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        interface = self.create_mock_gazette_interface(
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
                        "highlight_texts": ["test"],
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "highlight_texts": ["test"],
                    },
                ],
            )
        )
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_gazettes": 2,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today.strftime("%Y-%m-%d"),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "highlight_texts": ["test"],
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.strftime("%Y-%m-%d"),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "highlight_texts": ["test"],
                    },
                ],
            },
        )

    def test_api_with_none_edition_and_extra_field(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        interface = self.create_mock_gazette_interface(
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
                        "highlight_texts": ["test"],
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": None,
                        "edition": None,
                        "highlight_texts": ["test"],
                    },
                ],
            )
        )
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/gazettes/4205902")
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_id, "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_gazettes": 2,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today.strftime("%Y-%m-%d"),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "highlight_texts": ["test"],
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.strftime("%Y-%m-%d"),
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "highlight_texts": ["test"],
                    },
                ],
            },
        )

    def test_cities_endpoint_should_reject_request_without_partial_city_name(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/cities")
        self.assertNotEqual(response.status_code, 200)

    def test_cities_endpoint_should_accept_request_without_partial_city_name(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)

    def test_cities_should_return_some_city_info(self):
        configure_api_app(self.create_mock_gazette_interface(), MockSuggestionService())
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"cities": []},
        )

    def test_cities_should_request_data_from_gazette_interface(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(interface, MockSuggestionService())
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        interface.get_cities.assert_called_once()

    def test_cities_should_return_data_returned_by_gazettes_interface(self):
        configure_api_app(
            self.create_mock_gazette_interface(
                cities_info=[
                    {
                        "territory_id": "1234",
                        "territory_name": "piraporia",
                        "state_code": "SC",
                        "publication_urls": ["https://querido-diario.org.br"],
                        "level": "1",
                    }
                ]
            ),
            MockSuggestionService(),
        )
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
                    }
                ]
            },
        )

    def test_city_endpoint_should_accept_request_with_city_id(self):
        configure_api_app(
            self.create_mock_gazette_interface(
                city_info={
                    "territory_id": "1234",
                    "territory_name": "piraporia",
                    "state_code": "SC",
                    "publication_urls": ["https://querido-diario.org.br"],
                    "level": "1",
                }
            ),
            MockSuggestionService(),
        )
        client = TestClient(app)
        response = client.get("/cities/1234")
        self.assertEqual(response.status_code, 200)

    def test_city_endpoint_should_return_404_with_city_id_not_found(self):
        configure_api_app(
            self.create_mock_gazette_interface(), MockSuggestionService(),
        )
        client = TestClient(app)
        response = client.get("/cities/1234")
        self.assertEqual(response.status_code, 404)

    def test_city_endpoint_should_request_data_from_gazette_interface(self):
        interface = self.create_mock_gazette_interface(
            city_info={
                "territory_id": "1234",
                "territory_name": "piraporia",
                "state_code": "SC",
                "publication_urls": ["https://querido-diario.org.br"],
                "level": "1",
            }
        )
        configure_api_app(
            interface, MockSuggestionService(),
        )
        client = TestClient(app)
        response = client.get("/cities/1234")
        interface.get_city.assert_called_once()

    def test_city_endpoint_should_return_city_info_returned_by_gazettes_interface(self):
        configure_api_app(
            self.create_mock_gazette_interface(
                city_info={
                    "territory_id": "1234",
                    "territory_name": "piraporia",
                    "state_code": "SC",
                    "publication_urls": ["https://querido-diario.org.br"],
                    "level": "1",
                }
            ),
            MockSuggestionService(),
        )
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
                }
            },
        )


class ApiSuggestionsEndpointTests(TestCase):
    def setUp(self):
        self.suggestion_service = MockSuggestionService()
        configure_api_app(MockGazetteAccessInterface(), self.suggestion_service)
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
            configure_api_app(MockGazetteAccessInterface(), MagicMock())

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
            "/suggestions", json={"name": "My Name", "content": "Suggestion content",},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "email_address"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }

    def test_suggestion_endpoint_should_reject_when_name_is_not_present(self):
        response = self.client.post(
            "/suggestions",
            json={
                "email_address": "some-email-from@email.com",
                "content": "Suggestion content",
            },
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }

    def test_suggestion_endpoint_should_reject_when_content_is_not_present(self):
        response = self.client.post(
            "/suggestions",
            json={"email_address": "some-email-from@email.com", "name": "My Name",},
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "content"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }
