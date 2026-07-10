import os
from datetime import date, datetime
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import app, configure_api_app
from scraper import InvalidTerritoryIDException

from tests.test_helpers import (
    create_default_mocks,
    create_mock_scraper_interface,
)

TEST_API_KEY = "test-api-key"
TEST_API_KEY_HEADERS = {"X-API-Key": TEST_API_KEY}


class ScraperApiTestCase(TestCase):
    def setUp(self):
        self.scraper_interface = create_mock_scraper_interface()
        mocks = create_default_mocks()
        configure_api_app(*mocks[:6], self.scraper_interface)
        self.client = TestClient(app)
        self.env_patcher = patch.dict(
            os.environ, {"QUERIDO_DIARIO_SCRAPER_API_KEYS": TEST_API_KEY}
        )
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()


class ScraperApiAuthenticationTests(ScraperApiTestCase):
    def test_should_return_503_when_no_api_key_is_configured(self):
        with patch.dict(os.environ, {"QUERIDO_DIARIO_SCRAPER_API_KEYS": ""}):
            response = self.client.get(
                "/scraper/spiders", headers=TEST_API_KEY_HEADERS
            )
        self.assertEqual(response.status_code, 503)

    def test_should_return_503_when_api_key_env_var_is_absent(self):
        with patch.dict(os.environ):
            del os.environ["QUERIDO_DIARIO_SCRAPER_API_KEYS"]
            response = self.client.get(
                "/scraper/spiders", headers=TEST_API_KEY_HEADERS
            )
        self.assertEqual(response.status_code, 503)

    def test_should_return_401_when_api_key_header_is_missing(self):
        response = self.client.get("/scraper/spiders")
        self.assertEqual(response.status_code, 401)

    def test_should_return_403_when_api_key_is_invalid(self):
        response = self.client.get(
            "/scraper/spiders", headers={"X-API-Key": "wrong-key"}
        )
        self.assertEqual(response.status_code, 403)

    def test_should_accept_any_key_from_the_configured_list(self):
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_SCRAPER_API_KEYS": f"old-key,{TEST_API_KEY}"},
        ):
            response = self.client.get(
                "/scraper/spiders", headers={"X-API-Key": "old-key"}
            )
        self.assertEqual(response.status_code, 200)

    def test_all_scraper_endpoints_should_require_api_key(self):
        requests = [
            self.client.get("/scraper/spiders"),
            self.client.post("/scraper/gazettes", json={}),
            self.client.post("/scraper/job-stats", json={}),
            self.client.get("/scraper/job-stats"),
        ]
        for response in requests:
            self.assertEqual(response.status_code, 401)


class ScraperApiSpidersEndpointTests(ScraperApiTestCase):
    def test_spiders_endpoint_should_return_enabled_spiders(self):
        self.scraper_interface.get_enabled_spiders.return_value = [
            {
                "spider_name": "sp_campinas",
                "date_from": date(2015, 1, 1),
                "date_to": None,
            },
            {
                "spider_name": "ba_salvador",
                "date_from": date(2010, 6, 14),
                "date_to": None,
            },
        ]
        response = self.client.get("/scraper/spiders", headers=TEST_API_KEY_HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_spiders": 2,
                "spiders": [
                    {
                        "spider_name": "sp_campinas",
                        "date_from": "2015-01-01",
                        "date_to": None,
                    },
                    {
                        "spider_name": "ba_salvador",
                        "date_from": "2010-06-14",
                        "date_to": None,
                    },
                ],
            },
        )

    def test_spiders_endpoint_should_forward_date_filters_to_interface(self):
        response = self.client.get(
            "/scraper/spiders",
            headers=TEST_API_KEY_HEADERS,
            params={"start_date": "2024-01-01", "end_date": "2024-12-31"},
        )
        self.assertEqual(response.status_code, 200)
        self.scraper_interface.get_enabled_spiders.assert_called_once_with(
            date(2024, 1, 1), date(2024, 12, 31)
        )

    def test_spiders_endpoint_should_accept_request_without_date_filters(self):
        response = self.client.get("/scraper/spiders", headers=TEST_API_KEY_HEADERS)
        self.assertEqual(response.status_code, 200)
        self.scraper_interface.get_enabled_spiders.assert_called_once_with(None, None)

    def test_spiders_endpoint_should_fail_with_invalid_date_filter(self):
        response = self.client.get(
            "/scraper/spiders",
            headers=TEST_API_KEY_HEADERS,
            params={"start_date": "foo-bar-2222"},
        )
        self.assertEqual(response.status_code, 422)


def build_gazette_payload(**kwargs):
    payload = {
        "territory_id": "3550308",
        "date": "2024-06-01",
        "scraped_at": "2024-06-02T03:04:05",
        "file_path": "3550308/2024-06-01/abc123",
        "file_url": "https://example.com/gazette.pdf",
        "file_checksum": "abc123",
        "edition_number": "42",
        "is_extra_edition": False,
        "power": "executive",
    }
    payload.update(kwargs)
    return payload


class ScraperApiGazettesEndpointTests(ScraperApiTestCase):
    def test_gazettes_endpoint_should_create_gazette(self):
        self.scraper_interface.create_gazette.return_value = 123
        response = self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=build_gazette_payload(),
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"status": "created", "gazette_id": 123})

    def test_gazettes_endpoint_should_forward_gazette_data_to_interface(self):
        response = self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=build_gazette_payload(),
        )
        self.assertEqual(response.status_code, 201)
        self.scraper_interface.create_gazette.assert_called_once()
        gazette = self.scraper_interface.create_gazette.call_args.args[0]
        self.assertEqual(gazette["territory_id"], "3550308")
        self.assertEqual(gazette["date"], date(2024, 6, 1))
        self.assertEqual(gazette["scraped_at"], datetime(2024, 6, 2, 3, 4, 5))
        self.assertEqual(gazette["file_checksum"], "abc123")
        self.assertEqual(gazette["edition_number"], "42")
        self.assertEqual(gazette["is_extra_edition"], False)
        self.assertEqual(gazette["power"], "executive")
        self.assertIsNone(gazette["source_text"])

    def test_gazettes_endpoint_should_return_200_for_duplicated_gazette(self):
        self.scraper_interface.create_gazette.return_value = None
        response = self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=build_gazette_payload(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "duplicate"})

    def test_gazettes_endpoint_should_return_404_for_invalid_territory(self):
        self.scraper_interface.create_gazette.side_effect = InvalidTerritoryIDException(
            'Territory "0000000" does not exist.'
        )
        response = self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=build_gazette_payload(territory_id="0000000"),
        )
        self.assertEqual(response.status_code, 404)

    def test_gazettes_endpoint_should_fail_with_malformed_territory_id(self):
        response = self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=build_gazette_payload(territory_id="12345"),
        )
        self.assertEqual(response.status_code, 422)

    def test_gazettes_endpoint_should_fail_with_missing_required_fields(self):
        payload = build_gazette_payload()
        del payload["file_checksum"]
        response = self.client.post(
            "/scraper/gazettes",
            headers=TEST_API_KEY_HEADERS,
            json=payload,
        )
        self.assertEqual(response.status_code, 422)


class ScraperApiJobStatsEndpointTests(ScraperApiTestCase):
    def test_job_stats_endpoint_should_create_job_stats(self):
        self.scraper_interface.create_job_stats.return_value = 7
        response = self.client.post(
            "/scraper/job-stats",
            headers=TEST_API_KEY_HEADERS,
            json={
                "spider_name": "sp_campinas",
                "job_id": "123/4/5",
                "stats": {"item_scraped_count": 10},
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"status": "created", "job_stats_id": 7})
        self.scraper_interface.create_job_stats.assert_called_once_with(
            "sp_campinas", "123/4/5", {"item_scraped_count": 10}
        )

    def test_job_stats_endpoint_should_accept_request_without_job_id(self):
        response = self.client.post(
            "/scraper/job-stats",
            headers=TEST_API_KEY_HEADERS,
            json={"spider_name": "sp_campinas", "stats": {}},
        )
        self.assertEqual(response.status_code, 201)
        self.scraper_interface.create_job_stats.assert_called_once_with(
            "sp_campinas", None, {}
        )

    def test_job_stats_endpoint_should_fail_without_stats(self):
        response = self.client.post(
            "/scraper/job-stats",
            headers=TEST_API_KEY_HEADERS,
            json={"spider_name": "sp_campinas"},
        )
        self.assertEqual(response.status_code, 422)

    def test_job_stats_endpoint_should_return_job_stats(self):
        self.scraper_interface.get_job_stats.return_value = [
            {
                "id": 1,
                "spider_name": "sp_campinas",
                "job_id": "123/4/5",
                "stats": {"item_scraped_count": 10},
                "created_at": datetime(2024, 6, 2, 3, 4, 5),
            }
        ]
        response = self.client.get(
            "/scraper/job-stats", headers=TEST_API_KEY_HEADERS
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "total_stats": 1,
                "job_stats": [
                    {
                        "id": 1,
                        "spider_name": "sp_campinas",
                        "job_id": "123/4/5",
                        "stats": {"item_scraped_count": 10},
                        "created_at": "2024-06-02T03:04:05",
                    }
                ],
            },
        )

    def test_job_stats_endpoint_should_forward_filters_to_interface(self):
        response = self.client.get(
            "/scraper/job-stats",
            headers=TEST_API_KEY_HEADERS,
            params={"spider": "sp_campinas", "since": "2024-06-01T00:00:00"},
        )
        self.assertEqual(response.status_code, 200)
        self.scraper_interface.get_job_stats.assert_called_once_with(
            "sp_campinas", datetime(2024, 6, 1, 0, 0, 0)
        )
