"""
Tests for the utils.url_builder module.
"""

import os
import unittest
from unittest.mock import patch

from utils import build_file_url


class TestBuildFileUrl(unittest.TestCase):
    """
    Tests for the build_file_url utility function.
    """

    def test_relative_path_without_endpoint(self):
        """Test relative path without QUERIDO_DIARIO_FILES_ENDPOINT returns as-is"""
        with patch.dict(os.environ, {}, clear=True):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(result, "3304557/2019/file.pdf")

    def test_relative_path_with_endpoint(self):
        """Test relative path with QUERIDO_DIARIO_FILES_ENDPOINT builds full URL"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br"},
        ):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_relative_path_with_endpoint_with_protocol(self):
        """Test relative path with endpoint that includes protocol"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "https://data.queridodiario.ok.org.br"},
        ):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_relative_path_with_endpoint_trailing_slash(self):
        """Test relative path handles trailing slash correctly"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br/"},
        ):
            result = build_file_url("3304557/2019/file.pdf")
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_relative_path_with_leading_slash(self):
        """Test relative path with leading slash is handled correctly"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br"},
        ):
            result = build_file_url("/3304557/2019/file.pdf")
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_full_url_without_replace_flag(self):
        """Test full URL without REPLACE_FILE_URL_BASE returns as-is (legacy mode)"""
        with patch.dict(
            os.environ,
            {"QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br"},
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(result, original_url)

    def test_full_url_with_replace_flag_false(self):
        """Test full URL with REPLACE_FILE_URL_BASE=false returns as-is"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "false",
            },
        ):
            original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(original_url)
            self.assertEqual(result, original_url)

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

    def test_replace_flag_case_insensitive(self):
        """Test REPLACE_FILE_URL_BASE is case insensitive"""
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "TrUe",
            },
        ):
            old_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
            result = build_file_url(old_url)
            self.assertEqual(
                result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
            )

    def test_endpoint_without_protocol_gets_https(self):
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
            self.assertTrue(result.startswith("https://"))
            self.assertIn("data.queridodiario.ok.org.br", result)

    def test_url_duplication_prevention(self):
        """Test that URLs with endpoint already in path don't get duplicated

        This tests the bug where https://data.queridodiario.ok.org.br/data.queridodiario.ok.org.br/...
        was being generated instead of https://data.queridodiario.ok.org.br/...
        """
        with patch.dict(
            os.environ,
            {
                "QUERIDO_DIARIO_FILES_ENDPOINT": "data.queridodiario.ok.org.br",
                "REPLACE_FILE_URL_BASE": "true",
            },
        ):
            # URL that already has the correct endpoint should NOT be modified
            correct_url = "https://data.queridodiario.ok.org.br/3168002/2026-01-13/e55c343644b1fc6bd8788fd6cc9726e81dfdfffc.pdf"
            result = build_file_url(correct_url)

            # Should return exactly the same URL, not duplicate the domain
            self.assertEqual(result, correct_url)

            # Ensure domain is NOT duplicated
            self.assertEqual(result.count("data.queridodiario.ok.org.br"), 1)

            # Ensure it doesn't contain the duplicated pattern
            self.assertNotIn(
                "data.queridodiario.ok.org.br/data.queridodiario.ok.org.br", result
            )


if __name__ == "__main__":
    unittest.main()
