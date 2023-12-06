from unittest import TestCase

from unittest.mock import patch

from config import load_configuration


class BasicConfigurationTests(TestCase):
    def check_configuration_values(self, configuration, expected_values):
        self.assertEqual(
            configuration.host,
            expected_values["QUERIDO_DIARIO_OPENSEARCH_HOST"],
            msg="Invalid opensearch host",
        )
        self.assertEqual(
            configuration.index,
            expected_values["QUERIDO_DIARIO_OPENSEARCH_INDEX"],
            msg="Invalid opensearch index",
        )
        self.assertEqual(
            configuration.root_path,
            expected_values["QUERIDO_DIARIO_API_ROOT_PATH"],
            msg="Invalid API root path",
        )
        self.assertEqual(
            configuration.url_prefix,
            expected_values["QUERIDO_DIARIO_URL_PREFIX"],
            msg="Invalid URL prefix",
        )
        self.assertEqual(
            configuration.cors_allow_origins,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_ORIGINS"],
        )
        self.assertEqual(
            configuration.cors_allow_credentials,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS"],
        )
        self.assertEqual(
            configuration.cors_allow_methods,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_METHODS"],
        )
        self.assertEqual(
            configuration.cors_allow_headers,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_HEADERS"],
        )

    @patch.dict(
        "os.environ", {}, True,
    )
    def test_load_configuration_with_no_envvars(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": ["*"],
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": True,
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": ["*"],
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": ["*"],
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)

    @patch.dict(
        "os.environ",
        {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": "",
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": "",
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": "",
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": "",
        },
        True,
    )
    def test_load_configuration_with_empty_envvars(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": [""],
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": True,
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": [""],
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": [""],
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)

    @patch.dict(
        "os.environ",
        {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "000.0.0.0",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "myindex",
            "QUERIDO_DIARIO_API_ROOT_PATH": "api/",
            "QUERIDO_DIARIO_URL_PREFIX": "https://test.com",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": "localhost",
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": "True",
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": "GET,POST",
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": "X-Test-Test",
        },
        True,
    )
    def test_load_configuration_with_envvars_defined(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "000.0.0.0",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "myindex",
            "QUERIDO_DIARIO_API_ROOT_PATH": "api/",
            "QUERIDO_DIARIO_URL_PREFIX": "https://test.com",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": ["localhost"],
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": True,
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": ["GET", "POST"],
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": ["X-Test-Test"],
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)
