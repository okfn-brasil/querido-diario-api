"""
Tests for build_file_url integration with themed excerpt objects.
"""

from unittest.mock import MagicMock

from themed_excerpts.themed_excerpt_access import ThemedExcerptSearchEngineGateway
from index import SearchEngineInterface
from utils import build_file_url
from tests.test_url_builder_base import BaseUrlBuilderTest


class TestThemedExcerptUrlBuilder(BaseUrlBuilderTest):
    """
    Tests for URL transformation in themed excerpt objects.
    """

    def setUp(self):
        """Set up mock gateway and common configuration"""
        super().setUp()
        self.mock_engine = MagicMock(spec=SearchEngineInterface)
        self.mock_engine.index_exists.return_value = True
        self.mock_query_builder = MagicMock()

        self.gateway = ThemedExcerptSearchEngineGateway(
            search_engine=self.mock_engine,
            query_builder=self.mock_query_builder,
        )
        self.endpoint = "cdn.queridodiario.ok.org.br"

    def _create_excerpt_hit(self, url, txt_url=None):
        """Helper to create a themed excerpt hit object"""
        hit = {
            "_source": {
                "excerpt_id": "excerpt123",
                "source_territory_id": "3304557",
                "source_date": "2019-01-01",
                "source_scraped_at": "2019-01-02T00:00:00",
                "source_url": url,
                "source_territory_name": "Rio de Janeiro",
                "source_state_code": "RJ",
                "excerpt_subthemes": ["subtheme1"],
                "excerpt": "Test excerpt content",
                "excerpt_entities": [],
            }
        }
        if txt_url is not None:
            hit["_source"]["source_file_raw_txt"] = txt_url
        return hit

    def test_excerpt_url_transformation(self):
        """Test that themed excerpt objects apply URL transformation"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )

        excerpt_hit = self._create_excerpt_hit(
            url="https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
            txt_url="https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.txt",
        )

        result = self.gateway._assemble_themed_excerpt_object(excerpt_hit, "test_theme")

        self.assert_url_equals(
            result.url, f"https://{self.endpoint}/3304557/2019/file.pdf"
        )
        self.assert_url_equals(
            result.txt_url, f"https://{self.endpoint}/3304557/2019/file.txt"
        )

    def test_excerpt_without_txt_url(self):
        """Test that themed excerpt objects handle missing txt_url"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )

        excerpt_hit = self._create_excerpt_hit(
            url="https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        )

        result = self.gateway._assemble_themed_excerpt_object(excerpt_hit, "test_theme")

        self.assert_url_equals(
            result.url, f"https://{self.endpoint}/3304557/2019/file.pdf"
        )
        self.assertIsNone(result.txt_url)

    def test_excerpt_with_relative_paths(self):
        """Test that themed excerpt objects work with relative paths (new data)"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}")

        excerpt_hit = self._create_excerpt_hit(
            url="3304557/2019/file.pdf", txt_url="3304557/2019/file.txt"
        )

        result = self.gateway._assemble_themed_excerpt_object(excerpt_hit, "test_theme")

        self.assert_url_equals(
            result.url, f"https://{self.endpoint}/3304557/2019/file.pdf"
        )
        self.assert_url_equals(
            result.txt_url, f"https://{self.endpoint}/3304557/2019/file.txt"
        )

    def test_excerpt_legacy_mode(self):
        """Test that themed excerpt objects preserve URLs in legacy mode"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="false",
        )

        original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        original_txt = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.txt"

        excerpt_hit = self._create_excerpt_hit(url=original_url, txt_url=original_txt)

        result = self.gateway._assemble_themed_excerpt_object(excerpt_hit, "test_theme")

        self.assert_url_equals(result.url, original_url)
        self.assert_url_equals(result.txt_url, original_txt)


class TestThemedExcerptUrlBuilderDirectCalls(BaseUrlBuilderTest):
    """
    Direct tests for build_file_url with themed excerpt scenarios.
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

    def test_legacy_url_without_replace_flag(self):
        """Test legacy URL without replace flag is preserved"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}")
        original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        result = build_file_url(original_url)
        self.assert_url_equals(result, original_url)

    def test_legacy_url_with_replace_flag(self):
        """Test legacy URL with replace flag is transformed"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=f"https://{self.endpoint}",
            REPLACE_FILE_URL_BASE="true",
        )
        original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        result = build_file_url(original_url)
        self.assert_url_equals(result, f"https://{self.endpoint}/3304557/2019/file.pdf")
