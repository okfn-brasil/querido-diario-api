from unittest import TestCase

from unittest.mock import patch

from config import load_configuration


class BasicConfigurationTests(TestCase):
    def check_configuration_values(self, configuration, expected_values):
        self.assertEqual(
            configuration.host,
            expected_values["QUERIDO_DIARIO_ELASTICSEARCH_HOST"],
            msg="Invalid elasticsearch host",
        )
        self.assertEqual(
            configuration.index,
            expected_values["QUERIDO_DIARIO_ELASTICSEARCH_INDEX"],
            msg="Invalid elasticsearch index",
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

    @patch.dict(
        "os.environ", {}, True,
    )
    def test_load_configuration_with_no_envvars(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_ELASTICSEARCH_HOST": "",
            "QUERIDO_DIARIO_ELASTICSEARCH_INDEX": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)

    @patch.dict(
        "os.environ",
        {
            "QUERIDO_DIARIO_ELASTICSEARCH_HOST": "",
            "QUERIDO_DIARIO_ELASTICSEARCH_INDEX": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
        },
        True,
    )
    def test_load_configuration_with_empty_envvars(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_ELASTICSEARCH_HOST": "",
            "QUERIDO_DIARIO_ELASTICSEARCH_INDEX": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)

    @patch.dict(
        "os.environ",
        {
            "QUERIDO_DIARIO_ELASTICSEARCH_HOST": "000.0.0.0",
            "QUERIDO_DIARIO_ELASTICSEARCH_INDEX": "myindex",
            "QUERIDO_DIARIO_API_ROOT_PATH": "api/",
            "QUERIDO_DIARIO_URL_PREFIX": "https://test.com",
        },
        True,
    )
    def test_load_configuration_with_envvars_defined(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_ELASTICSEARCH_HOST": "000.0.0.0",
            "QUERIDO_DIARIO_ELASTICSEARCH_INDEX": "myindex",
            "QUERIDO_DIARIO_API_ROOT_PATH": "api/",
            "QUERIDO_DIARIO_URL_PREFIX": "https://test.com",
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)
