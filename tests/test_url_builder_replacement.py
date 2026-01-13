"""
Tests for build_file_url with URL transformation/replacement features.
"""

from utils import build_file_url
from tests.test_url_builder_base import BaseUrlBuilderTest


class TestBuildFileUrlReplacement(BaseUrlBuilderTest):
    """
    Tests for build_file_url URL replacement feature (legacy data migration).
    """

    def setUp(self):
        """Set up with common endpoint configuration"""
        super().setUp()
        self.endpoint = "data.queridodiario.ok.org.br"
        self.expected_base = f"https://{self.endpoint}"

    def test_full_url_without_replace_flag(self):
        """Test full URL without REPLACE_FILE_URL_BASE returns as-is (legacy mode)"""
        self.set_env(QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint)
        original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        result = build_file_url(original_url)
        self.assert_url_equals(result, original_url)

    def test_full_url_with_replace_flag_false(self):
        """Test full URL with REPLACE_FILE_URL_BASE=false returns as-is"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="false"
        )
        original_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        result = build_file_url(original_url)
        self.assert_url_equals(result, original_url)

    def test_digitalocean_url_transformed(self):
        """Test that DigitalOcean Spaces URLs are transformed"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="true"
        )
        old_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        result = build_file_url(old_url)
        self.assert_url_equals(result, f"{self.expected_base}/3304557/2019/file.pdf")

    def test_digitalocean_url_variant_transformed(self):
        """Test that DigitalOcean Spaces URL variant is also transformed"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="true"
        )
        old_url = "https://queridodiario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        result = build_file_url(old_url)
        self.assert_url_equals(result, f"{self.expected_base}/3304557/2019/file.pdf")

    def test_s3_historico_url_transformed(self):
        """Test that S3 okbr-qd-historico URLs are transformed"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="true"
        )
        s3_url = "s3://okbr-qd-historico/3304557/2019/file.pdf"
        result = build_file_url(s3_url)
        self.assert_url_equals(result, f"{self.expected_base}/3304557/2019/file.pdf")

    def test_url_already_correct_not_transformed(self):
        """Test that URLs with correct endpoint are preserved as-is"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="true"
        )
        correct_url = f"{self.expected_base}/3304557/2019/file.pdf"
        result = build_file_url(correct_url)
        self.assert_url_equals(result, correct_url)

    def test_external_url_not_transformed(self):
        """Test that external URLs (not old storage) are preserved"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="true"
        )
        external_url = "https://doweb.rio.rj.gov.br/portal/edicoes/download/4067"
        result = build_file_url(external_url)
        self.assert_url_equals(result, external_url)

    def test_replace_flag_case_insensitive(self):
        """Test REPLACE_FILE_URL_BASE is case insensitive"""
        test_cases = ["TrUe", "TRUE", "True", "tRuE"]
        old_url = "https://querido-diario.nyc3.cdn.digitaloceanspaces.com/3304557/2019/file.pdf"
        expected = f"{self.expected_base}/3304557/2019/file.pdf"

        for flag_value in test_cases:
            with self.subTest(flag_value=flag_value):
                self.set_env(
                    QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint,
                    REPLACE_FILE_URL_BASE=flag_value,
                )
                result = build_file_url(old_url)
                self.assert_url_equals(result, expected)

    def test_url_duplication_prevention(self):
        """Test that URLs with endpoint already in path don't get duplicated"""
        self.set_env(
            QUERIDO_DIARIO_FILES_ENDPOINT=self.endpoint, REPLACE_FILE_URL_BASE="true"
        )
        correct_url = f"{self.expected_base}/3168002/2026-01-13/e55c343644b1fc6bd8788fd6cc9726e81dfdfffc.pdf"
        result = build_file_url(correct_url)

        self.assert_url_equals(result, correct_url)
        self.assertEqual(
            result.count(self.endpoint), 1, "Domain should not be duplicated"
        )
        self.assertNotIn(
            f"{self.endpoint}/{self.endpoint}",
            result,
            "Domain should not appear twice consecutively",
        )
