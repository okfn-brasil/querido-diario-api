from datetime import date, timedelta, datetime
from unittest.mock import MagicMock, patch
from unittest import TestCase, expectedFailure

from fastapi.testclient import TestClient

from api import app, configure_api_app

from gazettes import GazetteAccessInterface, GazetteRequest
from suggestions import Suggestion, SuggestionSent, SuggestionServiceInterface
from companies import CompaniesAccessInterface
from aggregates import AggregatesAccessInterface
from themed_excerpts import ThemedExcerptAccessInterface
from cities import CityAccessInterface


@GazetteAccessInterface.register
class MockGazetteAccessInterface:
    pass


@SuggestionServiceInterface.register
class MockSuggestionService:
    pass


@CompaniesAccessInterface.register
class MockCompaniesAccessInterface:
    pass


@AggregatesAccessInterface.register
class MockAggregatesAccessInterface:
    pass


@ThemedExcerptAccessInterface.register
class MockThemedExcerptAccessInterface:
    pass


@CityAccessInterface.register
class MockCityAccessInterface:
    pass


class ApiGazettesEndpointTests(TestCase):
    def create_mock_gazette_interface(
        self, 
        return_value=(0, []), 
        cities_info=[], 
        city_info=None
    ):
        interface = MockGazetteAccessInterface()
        interface.get_gazettes = MagicMock(return_value=return_value)
        interface.get_cities   = MagicMock(return_value=cities_info)
        interface.get_city     = MagicMock(return_value=city_info)
        return interface

    def get_test_client(self):
        configure_api_app(
            gazettes=self.create_mock_gazette_interface(),
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(),
        )
        return TestClient(app)

    def test_api_should_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        with self.assertRaises(Exception):
            configure_api_app(
                MagicMock(), MockSuggestionService(), MockCompaniesAccessInterface()
            )

    def test_api_should_not_fail_when_try_to_set_any_object_as_gazettes_interface(self):
        configure_api_app(
            gazettes=MockGazetteAccessInterface(),
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )

    def test_gazettes_endpoint_should_accept_territory_id_in_the_path(self):
        interface = self.create_mock_gazette_interface() 

        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )

        client = TestClient(app)
        response = client.get("/gazettes?territory_ids=4205902")


        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            "4205902", interface.get_gazettes.call_args.args[0].territory_ids[0]
        )
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_until)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].scraped_since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].scraped_until)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].querystring)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].offset)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].size)

    def test_gazettes_endpoint_should_accept_query_published_since_date(self):
        client = self.get_test_client()

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"published_since": date.today().strftime("%Y-%m-%d")}
        )

        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_published_until_date(self):
        client = self.get_test_client()

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"published_until": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_scraped_since_date(self):
        client = self.get_test_client()

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"scraped_since": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_accept_query_scraped_until_date(self):
        client = self.get_test_client()

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"scraped_until": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_endpoint_should_fail_with_invalid_published_since_value(self):
        client = self.get_test_client()

        response = client.get("/gazettes?territory_ids=4205902", params={"published_since": "foo-bar-2222"})
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_published_until_value(self):
        
        client = self.get_test_client()

        response = client.get("/gazettes?territory_ids=4205902", params={"published_until": "foo-bar-2222"})

        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_scraped_since_value(self):
        
        client = self.get_test_client()

        response = client.get("/gazettes?territory_ids=4205902", params={"scraped_until": "foo-bar-2222"})

        self.assertEqual(response.status_code, 422)
    
    def test_gazettes_endpoint_should_fail_with_invalid_scraped_until_value(self):
        
        client = self.get_test_client()

        response = client.get("/gazettes?territory_ids=4205902", params={"scraped_until": "foo-bar-2222"})

        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_invalid_pagination_data(self):
        client = self.get_test_client()

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"offset": "asfasdasd", "size": "10"}
        )

        self.assertEqual(response.status_code, 422)

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"offset": "10", "size": "ssddsfds"}
        )

        self.assertEqual(response.status_code, 422)

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"offset": "x", "size": "asdasdas"}
        )

        self.assertEqual(response.status_code, 422)

    def test_get_gazettes_without_territory_id_should_be_fine(self):
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        client = TestClient(app)
        response = client.get("/gazettes")
        
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].published_until)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].scraped_since)
        self.assertIsNone(interface.get_gazettes.call_args.args[0].scraped_until)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].querystring)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].offset)
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].size)

    def test_get_gazettes_should_request_gazettes_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        client = TestClient(app)

        response = client.get("/gazettes?territory_ids=4205902")
        
        self.assertEqual(response.status_code, 200)

        interface.get_gazettes.assert_called_once()

    def test_get_gazettes_should_forward_gazettes_filters_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )

        client = TestClient(app)

        today = date.today().strftime("%Y-%m-%d")
        datetime_now   = datetime.now().replace(microsecond=0).isoformat()


        response = client.get(
            "/gazettes?territory_ids=4205902",
            params={
                "published_since": today,
                "published_until": today,
                "scraped_since": datetime_now,
                "scraped_until": datetime_now,
                "offset": 10,
                "size": 100,
            },
        )

        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids[0], "4205902"
        )
        self.assertEqual(interface.get_gazettes.call_args.args[0].published_since, date.today())
        self.assertEqual(interface.get_gazettes.call_args.args[0].published_until, date.today())
        self.assertEqual(interface.get_gazettes.call_args.args[0].scraped_since, datetime.now().replace(microsecond=0))
        self.assertEqual(interface.get_gazettes.call_args.args[0].scraped_until, datetime.now().replace(microsecond=0))
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 10)
        self.assertEqual(interface.get_gazettes.call_args.args[0].size, 100)


    def test_get_gazettes_should_return_json_with_items(self):
        today = date.today()

        formatted_datetime_now = datetime.now().isoformat()
        
        interface = self.create_mock_gazette_interface(
            (
                1,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "scraped_at": formatted_datetime_now,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/",
                    }
                ],
            )
        )

        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        client = TestClient(app)
        
        response = client.get("/gazettes?territory_ids=4205902")
        interface.get_gazettes.assert_called_once()
        
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids[0], "4205902"
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
                        "scraped_at": formatted_datetime_now, 
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state", 
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/",
                    }
                ],
            },
        )

    def test_get_gazettes_should_return_empty_list_when_no_gazettes_is_found(self):
        
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        client   = TestClient(app)
        
        response = client.get("/gazettes?territory_ids=4205902")
        
        interface.get_gazettes.assert_called_once()
        
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids[0], "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"total_gazettes": 0, "gazettes": []},
        )

    def test_gazettes_endpoint_should_accept_query_querystring_date(self):
        client = self.get_test_client()

        response = client.get(
            "/gazettes?territory_ids=4205902", params={"querystring": "keyword1 keyword2"}
        )
        self.assertEqual(response.status_code, 200)
        response = client.get("/gazettes?territory_ids=4205902", params={"querystring": []})
        self.assertEqual(response.status_code, 200)

    def test_get_gazettes_should_forward_querystring_to_interface_object(self): #TODO: separar os testes
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        client = TestClient(app)

        response = client.get(
            "/gazettes?terriotry_ids=4205902", params={"querystring": "keyword1 1 True"}
        )

        interface.get_gazettes.assert_called_once()

        self.assertEqual(
            interface.get_gazettes.call_args.args[0].querystring, "keyword1 1 True"
        )
        
        # --------------------------------------------------

        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        response = client.get("/gazettes?territory_ids=4205902", params={"querystring": None})
        interface.get_gazettes.assert_called_once()
        
        self.assertIsNotNone(interface.get_gazettes.call_args.args[0].querystring)
        
        # ----------------------------------------------------

        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )

        response = client.get("/gazettes?territory_ids=4205902", params={"querystring": ""})
        interface.get_gazettes.assert_called_once()
        
        self.assertEqual(interface.get_gazettes.call_args.args[0].querystring, "")

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_published_since_date(self):
        client = self.get_test_client()
        
        response = client.get(
            "/gazettes", params={"published_since": date.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_published_until_date(self):
        client = self.get_test_client()
        
        response = client.get(
            "/gazettes", params={"published_until": date.today().strftime("%Y-%m-%d")}
        )
        
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_scraped_since_date(self):
        client = self.get_test_client()
        
        response = client.get(
            "/gazettes", params={"scraped_since":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        )
        
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_ids_endpoint_should_accept_query_scraped_until_date(self):
        client = self.get_test_client()
        
        response = client.get(
            "/gazettes", params={"scraped_until": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
        )
        
        self.assertEqual(response.status_code, 200)

    def test_gazettes_without_territory_ids_endpoint_should_fail_with_invalid_published_since_value(self):
        client = self.get_test_client()

        response = client.get("/gazettes", params={"published_since": "foo-bar-2222"})
        
        self.assertEqual(response.status_code, 422)

    def test_gazettes_without_territory_ids_endpoint_should_fail_with_invalid_published_until_value(self):
        client = self.get_test_client()

        response = client.get("/gazettes", params={"published_until": "foo-bar-2222"})
        
        self.assertEqual(response.status_code, 422)
    
    def test_gazettes_without_territory_ids_endpoint_should_fail_with_invalid_scraped_since_value(self):
        client = self.get_test_client()

        response = client.get("/gazettes", params={"scraped_since": "foo-bar-2222"})
        
        self.assertEqual(response.status_code, 422)

    def test_gazettes_without_territory_ids_endpoint_should_fail_with_invalid_scraped_until_value(self):
        client = self.get_test_client()

        response = client.get("/gazettes", params={"scraped_until": "foo-bar-2222"})
        
        self.assertEqual(response.status_code, 422)    

    def test_get_gazettes_without_territory_id_should_forward_gazettes_filters_to_interface_object(self):
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )
        
        client = TestClient(app)
        
        response = client.get(
            "/gazettes",
            params={
                "published_since": date.today().strftime("%Y-%m-%d"),
                "published_until": date.today().strftime("%Y-%m-%d"),
                "scraped_since": datetime.now().replace(microsecond=0).isoformat(),
                "scraped_until": datetime.now().replace(microsecond=0).isoformat(),
                "offset": 10,
                "size": 100,
            },
        )
        
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].territory_ids, [])
        self.assertEqual(interface.get_gazettes.call_args.args[0].published_since, date.today())
        self.assertEqual(interface.get_gazettes.call_args.args[0].published_until, date.today())
        self.assertEqual(interface.get_gazettes.call_args.args[0].scraped_since, datetime.now().replace(microsecond=0))
        self.assertEqual(interface.get_gazettes.call_args.args[0].scraped_until, datetime.now().replace(microsecond=0)) 
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 10)
        self.assertEqual(interface.get_gazettes.call_args.args[0].size, 100)

    def test_api_should_forward_the_result_offset(self):
        interface = self.create_mock_gazette_interface()
        
        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(), 
        )

        client = TestClient(app)
        
        response = client.get("/gazettes", params={"offset": 0,})
        
        self.assertEqual(response.status_code, 200)
        interface.get_gazettes.assert_called_once()
        self.assertEqual(interface.get_gazettes.call_args.args[0].offset, 0)

    @expectedFailure
    def test_configure_api_should_failed_with_invalid_root_path(self):
        configure_api_app(
            gazettes=MockGazetteAccessInterface(),
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(),
            api_root_path=1,
        )

    def test_configure_api_root_path(self):
        configure_api_app(
            gazettes=MockGazetteAccessInterface(),
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(),
            api_root_path="/api/v1",
        )

        self.assertEqual("/api/v1", app.root_path)

    def test_api_without_edition_and_extra_field(self):
        today = date.today()
        yesterday = today - timedelta(days=1)

        scraped_at = datetime.now().isoformat()
        yesterday_scraped_at = (datetime.now() - timedelta(days=1)).isoformat()

        interface = self.create_mock_gazette_interface(
            (
                2,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "scraped_at": scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday,
                        "scraped_at": yesterday_scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/"
                    },
                ],
            )
        )

        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(),
            api_root_path="/api/v1",
        )

        client = TestClient(app)
        
        response = client.get("/gazettes?territory_ids=4205902")
        
        interface.get_gazettes.assert_called_once()
        
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids[0], "4205902"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_gazettes": 2,
                "gazettes": [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "scraped_at": scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.strftime("%Y-%m-%d"),
                        "scraped_at": yesterday_scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/"
                    },
                ],
            },
        )

    def test_api_with_none_edition_and_extra_field(self):
        today = date.today()
        yesterday = today - timedelta(days=1)

        scraped_at = datetime.now().isoformat()
        yesterday_scraped_at = (datetime.now() - timedelta(days=1)).isoformat()

        interface = self.create_mock_gazette_interface(
            (
                2,
                [
                    {
                        "territory_id": "4205902",
                        "date": today,
                        "scraped_at": scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday,
                        "scraped_at": yesterday_scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": None,
                        "edition": None,
                        "txt_url": "https://queridodiario.ok.org.br/",
                    },
                ],
            )
        )

        configure_api_app(
            gazettes=interface,
            themed_excerpts=MockThemedExcerptAccessInterface(),
            cities=MockCityAccessInterface(),
            suggestion_service=MockSuggestionService(),
            companies=MockCompaniesAccessInterface(),
            aggregates=MockAggregatesAccessInterface(),
        )

        client = TestClient(app)
        
        response = client.get("/gazettes?territory_ids=4205902")
        interface.get_gazettes.assert_called_once()
        
        self.assertEqual(
            interface.get_gazettes.call_args.args[0].territory_ids[0], "4205902"
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
                        "scraped_at": scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "is_extra_edition": False,
                        "edition": "12.3442",
                        "txt_url": "https://queridodiario.ok.org.br/",
                    },
                    {
                        "territory_id": "4205902",
                        "date": yesterday.strftime("%Y-%m-%d"),
                        "scraped_at": yesterday_scraped_at,
                        "url": "https://queridodiario.ok.org.br/",
                        "territory_name": "My city",
                        "state_code": "My state",
                        "excerpts": [],
                        "txt_url": "https://queridodiario.ok.org.br/"
                    },
                ],
            },
        )

    def test_cities_endpoint_should_reject_request_without_partial_city_name(self):
        client = self.get_test_client()
        
        response = client.get("/cities")

        self.assertNotEqual(response.status_code, 200)

    def test_cities_endpoint_should_accept_request_without_partial_city_name(self):
        configure_api_app(
            self.create_mock_gazette_interface(),
            MockSuggestionService(),
            MockCompaniesAccessInterface(),
        )
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)

    def test_cities_should_return_some_city_info(self):
        configure_api_app(
            self.create_mock_gazette_interface(),
            MockSuggestionService(),
            MockCompaniesAccessInterface(),
        )
        client = TestClient(app)
        response = client.get("/cities", params={"city_name": "pirapo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"cities": []},
        )

    def test_cities_should_request_data_from_gazette_interface(self):
        interface = self.create_mock_gazette_interface()
        configure_api_app(
            interface, MockSuggestionService(), MockCompaniesAccessInterface()
        )
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
            MockCompaniesAccessInterface(),
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
            MockCompaniesAccessInterface(),
        )
        client = TestClient(app)
        response = client.get("/cities/1234")
        self.assertEqual(response.status_code, 200)

    def test_city_endpoint_should_return_404_with_city_id_not_found(self):
        configure_api_app(
            self.create_mock_gazette_interface(),
            MockSuggestionService(),
            MockCompaniesAccessInterface(),
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
            interface, MockSuggestionService(), MockCompaniesAccessInterface(),
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
            MockCompaniesAccessInterface(),
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
        configure_api_app(
            MockGazetteAccessInterface(),
            self.suggestion_service,
            MockCompaniesAccessInterface(),
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
                MockCompaniesAccessInterface(),
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
