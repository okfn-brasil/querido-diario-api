import os
import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from gazettes.gazette_access import GazetteSearchEngineGateway
from index import SearchEngineInterface
from utils import build_file_url


class TestGazetteFileUrlBuilder(unittest.TestCase):
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

        self.gateway = GazetteSearchEngineGateway(
            search_engine=self.mock_engine,
            query_builder=self.mock_query_builder,
            index="test_index",
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

    def test_relative_path_with_endpoint_trailing_slash(self):
        """Test relative path handles trailing slash correctly"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br/"},
        ):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(
                result, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_relative_path_with_leading_slash(self):
        """Test relative path with leading slash is handled correctly"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br"},
        ):
            result = build_file_url("/3304557/2019/file.pdf")
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

    def test_full_url_with_replace_flag_false(self):
        """Test full URL with REPLACE_FILE_URL_BASE=false returns as-is"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "false",
            },
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(result, original_url)

    def test_full_url_with_replace_flag_true_https(self):
        """Test full URL with REPLACE_FILE_URL_BASE=true replaces base URL (https)"""
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

    def test_full_url_with_replace_flag_true_http(self):
        """Test full URL with REPLACE_FILE_URL_BASE=true replaces base URL (http)"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            original_url = "http://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(
                result, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_full_url_with_replace_flag_true_s3(self):
        """Test full URL with REPLACE_FILE_URL_BASE=true replaces base URL (s3)"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            original_url = "s3://okbr-qd-historico/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(
                result, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_replace_flag_case_insensitive(self):
        """Test REPLACE_FILE_URL_BASE is case insensitive"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "TrUe",
            },
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(
                result, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_assemble_gazette_object_applies_url_transformation(self):
        """Test that _assemble_gazette_object applies URL transformation to url field"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            gazette_hit = {
                "_source": {
                    "territory_id": "3304557",
                    "date": "2019-01-01",
                    "scraped_at": "2019-01-02T00:00:00",
                    "url": "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
                    "file_checksum": "abc123",
                    "territory_name": "Rio de Janeiro",
                    "state_code": "RJ",
                    "file_raw_txt": "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.txt",
                }
            }

            result = self.gateway._assemble_gazette_object(gazette_hit)

            # Verify both url and txt_url are transformed
            self.assertEqual(
                result.url, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
            self.assertEqual(
                result.txt_url,
                "https://cdn.queridodiario.ok.org.br/3304557/2019/file.txt",
            )

    def test_assemble_gazette_object_without_txt_url(self):
        """Test that _assemble_gazette_object handles missing file_raw_txt"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            gazette_hit = {
                "_source": {
                    "territory_id": "3304557",
                    "date": "2019-01-01",
                    "scraped_at": "2019-01-02T00:00:00",
                    "url": "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf",
                    "file_checksum": "abc123",
                    "territory_name": "Rio de Janeiro",
                    "state_code": "RJ",
                }
            }

            result = self.gateway._assemble_gazette_object(gazette_hit)

            # Verify url is transformed but txt_url is None
            self.assertEqual(
                result.url, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
            self.assertIsNone(result.txt_url)

    def test_assemble_gazette_object_with_relative_paths(self):
        """Test that _assemble_gazette_object works with relative paths (new data)"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://cdn.queridodiario.ok.org.br"},
        ):
            gazette_hit = {
                "_source": {
                    "territory_id": "3304557",
                    "date": "2019-01-01",
                    "scraped_at": "2019-01-02T00:00:00",
                    "url": "3304557/2019/file.pdf",
                    "file_checksum": "abc123",
                    "territory_name": "Rio de Janeiro",
                    "state_code": "RJ",
                    "file_raw_txt": "3304557/2019/file.txt",
                }
            }

            result = self.gateway._assemble_gazette_object(gazette_hit)

            # Verify both are built with endpoint
            self.assertEqual(
                result.url, "https://cdn.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )
            self.assertEqual(
                result.txt_url,
                "https://cdn.queridodiario.ok.org.br/3304557/2019/file.txt",
            )


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
            # URL already has correct domain - should not be transformed
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

    def test_external_url_not_transformed(self):
        """Test that external URLs (not old storage) are preserved"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            external_url = "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067"
            result = build_file_url(external_url)
            self.assertEqual(result, external_url)

    def test_endpoint_without_protocol(self):
        """Test that endpoint without protocol gets https:// added"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            old_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(old_url)
            # Should add https:// to endpoint
            self.assertTrue(result.startswith("https://"))
            self.assertIn("data.queridodiario.ok.org.br", result)
