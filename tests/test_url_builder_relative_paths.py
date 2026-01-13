"""
Tests for build_file_url with relative paths.
"""

from utils import build_file_url
from tests.test_url_builder_base import BaseUrlBuilderTest


class TestBuildFileUrlRelativePaths(BaseUrlBuilderTest):
    """
    Tests for build_file_url with relative paths (new data format).
    """

    def test_relative_path_without_endpoint(self):
        """Test relative path without QUERIDO_DIARIO_FILES_ENDPOINT returns as-is"""
        result = build_file_url("3304557/2019/file.pdf")
        self.assert_url_equals(result, "3304557/2019/file.pdf")

    def test_relative_path_with_endpoint(self):
        """Test relative path with QUERIDO_DIARIO_FILES_ENDPOINT builds full URL"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT="data.queridodiario.ok.org.br")
        result = build_file_url("3304557/2019/file.pdf")
        self.assert_url_equals(
            result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
        )

    def test_relative_path_with_endpoint_with_protocol(self):
        """Test relative path with endpoint that includes protocol"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT="https://data.queridodiario.ok.org.br"
        )
        result = build_file_url("3304557/2019/file.pdf")
        self.assert_url_equals(
            result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
        )

    def test_relative_path_with_endpoint_trailing_slash(self):
        """Test relative path handles trailing slash correctly"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT="data.queridodiario.ok.org.br/")
        result = build_file_url("3304557/2019/file.pdf")
        self.assert_url_equals(
            result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
        )

    def test_relative_path_with_leading_slash(self):
        """Test relative path with leading slash is handled correctly"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT="data.queridodiario.ok.org.br")
        result = build_file_url("/3304557/2019/file.pdf")
        self.assert_url_equals(
            result, "https://data.queridodiario.ok.org.br/3304557/2019/file.pdf"
        )

    def test_endpoint_without_protocol_gets_https(self):
        """Test that endpoint without protocol gets https:// added"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT="data.queridodiario.ok.org.br",
            REPLACE_FILE_URL_BASE="true",
        )
        result = build_file_url("3304557/2019/file.pdf")
        self.assertTrue(result.startswith("https://"))
        self.assertIn("data.queridodiario.ok.org.br", result)
