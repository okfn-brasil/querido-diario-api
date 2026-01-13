"""
Tests for build_file_url integration with gazette objects.
"""

from unittest.mock import MagicMock

from gazettes.gazette_access import GazetteSearchEngineGateway
from index import SearchEngineInterface
from utils import build_file_url
from tests.test_url_builder_base import BaseUrlBuilderTest


class TestGazetteUrlBuilder(BaseUrlBuilderTest):
    """
    Tests for URL transformation in gazette objects.
    """

    def setUp(self):
        """Set up mock gateway and common configuration"""
        super().setUp()
        self.mock_engine = MagicMock(spec=SearchEngineInterface)
        self.mock_engine.index_exists.return_value = True
        self.mock_query_builder = MagicMock()

        self.gateway = GazetteSearchEngineGateway(
            search_engine=self.mock_engine,
            query_builder=self.mock_query_builder,
            index="test_index",
        )
        self.endpoint = "cdn.queridodiario.ok.org.br"

    def _create_gazette_hit(self, url, txt_url=None):
        """Helper to create a gazette hit object"""
        hit = {
            "_source": {
                "territory_id": "3304557",
                "date": "2019-01-01",
                "scraped_at": "2019-01-02T00:00:00",
                "url": url,
                "file_checksum": "abc123",
                "territory_name": "Rio de Janeiro",
                "state_code": "RJ",
            }
        }
        if txt_url is not None:
            hit["_source"]["file_raw_txt"] = txt_url
        return hit

    def test_gazette_object_url_transformation(self):
        """Test that gazette objects apply URL transformation"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )

        gazette_hit = self._create_gazette_hit(
            url="https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
            txt_url="https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.txt",
        )

        result = self.gateway._assemble_gazette_object(gazette_hit)

        self.assert_url_equals(
            result.url, f"https://{self.endpoint}/3304557/2019/file.pdf"
        )
        self.assert_url_equals(
            result.txt_url, f"https://{self.endpoint}/3304557/2019/file.txt"
        )

    def test_gazette_object_without_txt_url(self):
        """Test that gazette objects handle missing txt_url"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )

        gazette_hit = self._create_gazette_hit(
            url="https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        )

        result = self.gateway._assemble_gazette_object(gazette_hit)

        self.assert_url_equals(
            result.url, f"https://{self.endpoint}/3304557/2019/file.pdf"
        )
        self.assertIsNone(result.txt_url)

    def test_gazette_object_with_relative_paths(self):
        """Test that gazette objects work with relative paths (new data)"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}")

        gazette_hit = self._create_gazette_hit(
            url="3304557/2019/file.pdf", txt_url="3304557/2019/file.txt"
        )

        result = self.gateway._assemble_gazette_object(gazette_hit)

        self.assert_url_equals(
            result.url, f"https://{self.endpoint}/3304557/2019/file.pdf"
        )
        self.assert_url_equals(
            result.txt_url, f"https://{self.endpoint}/3304557/2019/file.txt"
        )

    def test_gazette_object_multiple_protocols(self):
        """Test URL transformation with different protocols"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )

        test_cases = [
            (
                "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/file.pdf",
                "https",
            ),
            ("http://querido-diario.nyc3.cdn.digitaloceanspaces.com/file.pdf", "http"),
            ("s3://okbr-qd-historico/file.pdf", "s3"),
        ]

        for old_url, protocol in test_cases:
            with self.subTest(protocol=protocol):
                gazette_hit = self._create_gazette_hit(url=old_url)
                result = self.gateway._assemble_gazette_object(gazette_hit)
                self.assertTrue(result.url.startswith("https://"))
                self.assertIn(self.endpoint, result.url)


class TestGazetteUrlBuilderDirectCalls(BaseUrlBuilderTest):
    """
    Direct tests for build_file_url with gazette-specific scenarios.
    """

    def setUp(self):
        """Set up common endpoint"""
        super().setUp()
        self.endpoint = "cdn.queridodiario.ok.org.br"

    def test_relative_path_without_endpoint(self):
        """Test relative path without endpoint returns as-is"""
        result = build_file_url("3304557/2019/file.pdf")
        self.assert_url_equals(result, "3304557/2019/file.pdf")

    def test_relative_path_with_endpoint(self):
        """Test relative path with endpoint builds full URL"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}")
        result = build_file_url("3304557/2019/file.pdf")
        self.assert_url_equals(result, f"https://{self.endpoint}/3304557/2019/file.pdf")

    def test_full_url_transformations(self):
        """Test various old URLs are correctly transformed"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )

        old_urls = [
            "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
            "http://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
            "s3://okbr-qd-historico/3304557/2019/file.pdf",
        ]

        expected = f"https://{self.endpoint}/3304557/2019/file.pdf"

        for old_url in old_urls:
            with self.subTest(old_url=old_url):
                result = build_file_url(old_url)
                self.assert_url_equals(result, expected)
