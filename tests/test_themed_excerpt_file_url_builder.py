import os
import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from themed_excerpts.themed_excerpt_access import ThemedExcerptSearchEngineGateway
from index import SearchEngineInterface
from utils import build_file_url


class TestThemedExcerptFileUrlBuilder(unittest.TestCase):
    """
    Tests for the build_file_url utility function
    to ensure URL transformation works correctly with the REPLACE_FILE_URL_BASE
    feature flag.
    """

    def setUp(self):
        """Set up a mock gateway for testing"""
        self.mock_engine = MagicMock(spec=SearchEngineInterface)
        self.mock_engine.index_exists.return_value = True
        self.mock_query_builder = MagicMock()

        self.gateway = ThemedExcerptSearchEngineGateway(
            search_engine=self.mock_engine,
            query_builder=self.mock_query_builder,
        )

    def test_relative_path_without_endpoint(self):
        """Test relative path without QUERIDO_DIARIO_FILES_ENDPOINT returns as-is"""
        with patch.dict(os.environ, {}, clear=True):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(result, "3304557/2019/file.pdf")

    def test_relative_path_with_endpoint(self):
        """Test relative path with QUERIDO_DIARIO_FILES_ENDPOINT builds full URL"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br"},
        ):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(
                result, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_full_url_without_replace_flag(self):
        """Test full URL without REPLACE_FILE_URL_BASE returns as-is (legacy mode)"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br"},
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(result, original_url)

    def test_full_url_with_replace_flag_true(self):
        """Test full URL with REPLACE_FILE_URL_BASE=true replaces base URL"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(
                result, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_assemble_themed_excerpt_object_applies_url_transformation(self):
        """Test that _assemble_themed_excerpt_object applies URL transformation to source_url field"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            excerpt_hit = {
                "_source": {
                    "excerpt_id": "excerpt123",
                    "source_territory_id": "3304557",
                    "source_date": "2019-01-01",
                    "source_scraped_at": "2019-01-02T00:00:00",
                    "source_url": "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
                    "source_territory_name": "Rio de Janeiro",
                    "source_state_code": "RJ",
                    "excerpt_subthemes": ["subtheme1"],
                    "excerpt": "Test excerpt content",
                    "source_file_raw_txt": "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.txt",
                    "excerpt_entities": [],
                }
            }

            result = self.gateway._assemble_themed_excerpt_object(
                excerpt_hit, "test_theme"
            )

            # Verify both url and txt_url are transformed
            self.assertEqual(
                result.url, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
            self.assertEqual(
                result.txt_url,
                "https://cdn.queridodiario.ok.org.br/3304557/2019/file.txt",
            )

    def test_assemble_themed_excerpt_object_without_txt_url(self):
        """Test that _assemble_themed_excerpt_object handles missing source_file_raw_txt"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            excerpt_hit = {
                "_source": {
                    "excerpt_id": "excerpt123",
                    "source_territory_id": "3304557",
                    "source_date": "2019-01-01",
                    "source_scraped_at": "2019-01-02T00:00:00",
                    "source_url": "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
                    "source_territory_name": "Rio de Janeiro",
                    "source_state_code": "RJ",
                    "excerpt_subthemes": ["subtheme1"],
                    "excerpt": "Test excerpt content",
                }
            }

            result = self.gateway._assemble_themed_excerpt_object(
                excerpt_hit, "test_theme"
            )

            # Verify url is transformed but txt_url is None
            self.assertEqual(
                result.url, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
            self.assertIsNone(result.txt_url)

    def test_assemble_themed_excerpt_object_with_relative_paths(self):
        """Test that _assemble_themed_excerpt_object works with relative paths (new data)"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br"},
        ):
            excerpt_hit = {
                "_source": {
                    "excerpt_id": "excerpt123",
                    "source_territory_id": "3304557",
                    "source_date": "2019-01-01",
                    "source_scraped_at": "2019-01-02T00:00:00",
                    "source_url": "3304557/2019/file.pdf",
                    "source_territory_name": "Rio de Janeiro",
                    "source_state_code": "RJ",
                    "excerpt_subthemes": ["subtheme1"],
                    "excerpt": "Test excerpt content",
                    "source_file_raw_txt": "3304557/2019/file.txt",
                }
            }

            result = self.gateway._assemble_themed_excerpt_object(
                excerpt_hit, "test_theme"
            )

            # Verify both are built with endpoint
            self.assertEqual(
                result.url, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
            self.assertEqual(
                result.txt_url,
                "https://cdn.queridodiario.ok.org.br/3304557/2019/file.txt",
            )

    def test_assemble_themed_excerpt_object_legacy_mode(self):
        """Test that _assemble_themed_excerpt_object preserves URLs in legacy mode"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "false",
            },
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            original_txt = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.txt"

            excerpt_hit = {
                "_source": {
                    "excerpt_id": "excerpt123",
                    "source_territory_id": "3304557",
                    "source_date": "2019-01-01",
                    "source_scraped_at": "2019-01-02T00:00:00",
                    "source_url": original_url,
                    "source_territory_name": "Rio de Janeiro",
                    "source_state_code": "RJ",
                    "excerpt_subthemes": ["subtheme1"],
                    "excerpt": "Test excerpt content",
                    "source_file_raw_txt": original_txt,
                }
            }

            result = self.gateway._assemble_themed_excerpt_object(
                excerpt_hit, "test_theme"
            )

            # Verify URLs are preserved as-is
            self.assertEqual(result.url, original_url)
            self.assertEqual(result.txt_url, original_txt)


if __name__ == "__main__":
    unittest.main()

    def test_url_already_correct_not_transformed(self):
        """Test that URLs with correct endpoint are preserved as-is"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            correct_url = "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            result = build_file_url(correct_url)
            self.assertEqual(result, correct_url)

    def test_digitalocean_url_transformed(self):
        """Test that DigitalOcean Spaces URLs are transformed"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            old_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(old_url)
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_s3_historico_url_transformed(self):
        """Test that S3 okbr-qd-historico URLs are transformed"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            s3_url = "s3://okbr-qd-historico/3304557/2019/file.pdf"
            result = build_file_url(s3_url)
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
