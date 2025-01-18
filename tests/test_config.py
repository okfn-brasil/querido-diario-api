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
            msg="Invalid CORS allow origins",
        )

        self.assertEqual(
            configuration.cors_allow_credentials,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS"],
            msg="Invalid CORS allow credentials",
        )

        self.assertEqual(
            configuration.cors_allow_methods,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_METHODS"],
            msg="Invalid CORS allow methods",
        )

        self.assertEqual(
            configuration.cors_allow_headers,
            expected_values["QUERIDO_DIARIO_CORS_ALLOW_HEADERS"],
            msg="Invalid CORS allow headers",
        )

        self.assertEqual(
            configuration.suggestion_mailjet_rest_api_key,
            expected_values["QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY"],
            msg="Invalid suggestion mailjet rest API key",
        )

        self.assertEqual(
            configuration.suggestion_mailjet_rest_api_secret,
            expected_values["QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET"],
            msg="Invalid suggestion mailjet rest API secret",
        )

        self.assertEqual(
            configuration.suggestion_sender_name,
            expected_values["QUERIDO_DIARIO_SUGGESTION_SENDER_NAME"],
            msg="Invalid suggestion sender name",
        )

        self.assertEqual(
            configuration.suggestion_sender_email,
            expected_values["QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL"],
            msg="Invalid suggestion sender Email",
        )

        self.assertEqual(
            configuration.suggestion_recipient_name,
            expected_values["QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME"],
            msg="Invalid suggestion recipient name",
        )

        self.assertEqual(
            configuration.suggestion_recipient_email,
            expected_values["QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL"],
            msg="Invalid suggestion recipient Email",
        )

        self.assertEqual(
            configuration.suggestion_mailjet_custom_id,
            expected_values["QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID"],
            msg="Invalid suggestion mailjet custom ID",
        )

        self.assertEqual(
            configuration.city_database_file,
            expected_values["CITY_DATABASE_CSV"],
            msg="Invalid city database csv",
        )

        self.assertEqual(
            configuration.gazette_index,
            expected_values["GAZETTE_OPENSEARCH_INDEX"],
            msg="Invalid gazette index",
        )

        self.assertEqual(
            configuration.gazette_content_field,
            expected_values["GAZETTE_CONTENT_FIELD"],
            msg="Invalid gazette content field",
        )

        self.assertEqual(
            configuration.gazette_content_exact_field_suffix,
            expected_values["GAZETTE_CONTENT_EXACT_FIELD_SUFFIX"],
            msg="Invalid gazette content exact field suffix",
        )

        self.assertEqual(
            configuration.gazette_publication_date_field,
            expected_values["GAZETTE_PUBLICATION_DATE_FIELD"],
            msg="Invalid gazette publication date field",
        )

        self.assertEqual(
            configuration.gazette_scraped_at_field,
            expected_values["GAZETTE_SCRAPED_AT_FIELD"],
            msg="Invalid gazette scraped at field",
        )

        self.assertEqual(
            configuration.gazette_territory_id_field,
            expected_values["GAZETTE_TERRITORY_ID_FIELD"],
            msg="Invalid gazette territory ID field",
        )

        self.assertEqual(
            configuration.themed_excerpt_content_field,
            expected_values["THEMED_EXCERPT_CONTENT_FIELD"],
            msg="Invalid themed excerpt content field",
        )

        self.assertEqual(
            configuration.themed_excerpt_content_exact_field_suffix,
            expected_values["THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX"],
            msg="Invalid themed excerpt content exact field suffix",
        )

        self.assertEqual(
            configuration.themed_excerpt_publication_date_field,
            expected_values["THEMED_EXCERPT_PUBLICATION_DATE_FIELD"],
            msg="Invalid themed excerpt publication date field",
        )

        self.assertEqual(
            configuration.themed_excerpt_scraped_at_field,
            expected_values["THEMED_EXCERPT_SCRAPED_AT_FIELD"],
            msg="Invalid themed excerpt scraped at field",
        )

        self.assertEqual(
            configuration.themed_excerpt_territory_id_field,
            expected_values["THEMED_EXCERPT_TERRITORY_ID_FIELD"],
            msg="Invalid themed excerpt territory ID field",
        )

        self.assertEqual(
            configuration.themed_excerpt_entities_field,
            expected_values["THEMED_EXCERPT_ENTITIES_FIELD"],
            msg="Invalid themed excerpt entities field",
        )

        self.assertEqual(
            configuration.themed_excerpt_subthemes_field,
            expected_values["THEMED_EXCERPT_SUBTHEMES_FIELD"],
            msg="Invalid themed excerpt subthemes field",
        )

        self.assertEqual(
            configuration.themed_excerpt_embedding_score_field,
            expected_values["THEMED_EXCERPT_EMBEDDING_SCORE_FIELD"],
            msg="Invalid themed excerpt embedding score field",
        )

        self.assertEqual(
            configuration.themed_excerpt_tfidf_score_field,
            expected_values["THEMED_EXCERPT_TFIDF_SCORE_FIELD"],
            msg="Invalid themed excerpt TF-IDF score field",
        )

        self.assertEqual(
            configuration.themed_excerpt_fragment_size,
            expected_values["THEMED_EXCERPT_FRAGMENT_SIZE"],
            msg="Invalid themed excerpt fragment size",
        )

        self.assertEqual(
            configuration.themed_excerpt_number_of_fragments,
            expected_values["THEMED_EXCERPT_NUMBER_OF_FRAGMENTS"],
            msg="Invalid themed excerpt number of fragments",
        )

        self.assertEqual(
            configuration.companies_database_host,
            expected_values["POSTGRES_COMPANIES_HOST"],
            msg="Invalid Postgres companies host",
        )

        self.assertEqual(
            configuration.companies_database_db,
            expected_values["POSTGRES_COMPANIES_DB"],
            msg="Invalid Postgres companies database",
        )

        self.assertEqual(
            configuration.companies_database_user,
            expected_values["POSTGRES_COMPANIES_USER"],
            msg="Invalid Postgres companies user",
        )

        self.assertEqual(
            configuration.companies_database_pass,
            expected_values["POSTGRES_COMPANIES_PASSWORD"],
            msg="Invalid Postgres companies password",
        )

        self.assertEqual(
            configuration.companies_database_port,
            expected_values["POSTGRES_COMPANIES_PORT"],
            msg="Invalid Postgres companies port",
        )

        self.assertEqual(
            configuration.opensearch_user,
            expected_values["QUERIDO_DIARIO_OPENSEARCH_USER"],
            msg="Invalid OpenSearch user",
        )

        self.assertEqual(
            configuration.opensearch_pswd,
            expected_values["QUERIDO_DIARIO_OPENSEARCH_PASSWORD"],
            msg="Invalid OpenSearch password",
        )

        self.assertEqual(
            configuration.aggregates_database_host,
            expected_values["POSTGRES_AGGREGATES_HOST"],
            msg="Invalid Postgres aggregates host",
        )

        self.assertEqual(
            configuration.aggregates_database_db,
            expected_values["POSTGRES_AGGREGATES_DB"],
            msg="Invalid Postgres aggregates database",
        )

        self.assertEqual(
            configuration.aggregates_database_user,
            expected_values["POSTGRES_AGGREGATES_USER"],
            msg="Invalid Postgres aggregates user",
        )

        self.assertEqual(
            configuration.aggregates_database_pass,
            expected_values["POSTGRES_AGGREGATES_PASSWORD"],
            msg="Invalid Postgres aggregates password",
        )

        self.assertEqual(
            configuration.aggregates_database_port,
            expected_values["POSTGRES_AGGREGATES_PORT"],
            msg="Invalid Postgres aggregates port",
        )

    @patch.dict(
        "os.environ", {}, True,
    )
    def test_load_configuration_with_no_envvars(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": ["*"],
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": True,
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": ["*"],
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": ["*"],
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET": "",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_NAME": "",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL": "",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME": "",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID": "",
            "CITY_DATABASE_CSV": "",
            "GAZETTE_OPENSEARCH_INDEX": "",
            "GAZETTE_CONTENT_FIELD": "",
            "GAZETTE_CONTENT_EXACT_FIELD_SUFFIX": "",
            "GAZETTE_PUBLICATION_DATE_FIELD": "",
            "GAZETTE_SCRAPED_AT_FIELD": "",
            "GAZETTE_TERRITORY_ID_FIELD": "",
            "THEMES_DATABASE_JSON": "",
            "THEMED_EXCERPT_CONTENT_FIELD": "",
            "THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX": "",
            "THEMED_EXCERPT_PUBLICATION_DATE_FIELD": "",
            "THEMED_EXCERPT_SCRAPED_AT_FIELD": "",
            "THEMED_EXCERPT_TERRITORY_ID_FIELD": "",
            "THEMED_EXCERPT_ENTITIES_FIELD": "",
            "THEMED_EXCERPT_SUBTHEMES_FIELD": "",
            "THEMED_EXCERPT_EMBEDDING_SCORE_FIELD": "",
            "THEMED_EXCERPT_TFIDF_SCORE_FIELD": "",
            "THEMED_EXCERPT_FRAGMENT_SIZE": 10000,
            "THEMED_EXCERPT_NUMBER_OF_FRAGMENTS": 1,
            "POSTGRES_COMPANIES_HOST": "",
            "POSTGRES_COMPANIES_DB": "",
            "POSTGRES_COMPANIES_USER": "",
            "POSTGRES_COMPANIES_PASSWORD": "",
            "POSTGRES_COMPANIES_PORT": "",
            "QUERIDO_DIARIO_OPENSEARCH_USER": "",
            "QUERIDO_DIARIO_OPENSEARCH_PASSWORD": "",
            "POSTGRES_AGGREGATES_HOST": "",
            "POSTGRES_AGGREGATES_DB": "",
            "POSTGRES_AGGREGATES_USER": "",
            "POSTGRES_AGGREGATES_PASSWORD": "",
            "POSTGRES_AGGREGATES_PORT": "",
        }

        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)

    @patch.dict(
        "os.environ",
        {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": "",
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": "",
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": "",
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET": "",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_NAME": "",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL": "",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME": "",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID": "",
            "CITY_DATABASE_CSV": "",
            "GAZETTE_OPENSEARCH_INDEX": "",
            "GAZETTE_CONTENT_FIELD": "",
            "GAZETTE_CONTENT_EXACT_FIELD_SUFFIX": "",
            "GAZETTE_PUBLICATION_DATE_FIELD": "",
            "GAZETTE_SCRAPED_AT_FIELD": "",
            "GAZETTE_TERRITORY_ID_FIELD": "",
            "THEMES_DATABASE_JSON": "",
            "THEMED_EXCERPT_CONTENT_FIELD": "",
            "THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX": "",
            "THEMED_EXCERPT_PUBLICATION_DATE_FIELD": "",
            "THEMED_EXCERPT_SCRAPED_AT_FIELD": "",
            "THEMED_EXCERPT_TERRITORY_ID_FIELD": "",
            "THEMED_EXCERPT_ENTITIES_FIELD": "",
            "THEMED_EXCERPT_SUBTHEMES_FIELD": "",
            "THEMED_EXCERPT_EMBEDDING_SCORE_FIELD": "",
            "THEMED_EXCERPT_TFIDF_SCORE_FIELD": "",
            "THEMED_EXCERPT_FRAGMENT_SIZE": "",
            "THEMED_EXCERPT_NUMBER_OF_FRAGMENTS": "",
            "POSTGRES_COMPANIES_HOST": "",
            "POSTGRES_COMPANIES_DB": "",
            "POSTGRES_COMPANIES_USER": "",
            "POSTGRES_COMPANIES_PASSWORD": "",
            "POSTGRES_COMPANIES_PORT": "",
            "QUERIDO_DIARIO_OPENSEARCH_USER": "",
            "QUERIDO_DIARIO_OPENSEARCH_PASSWORD": "",
            "POSTGRES_AGGREGATES_HOST": "",
            "POSTGRES_AGGREGATES_DB": "",
            "POSTGRES_AGGREGATES_USER": "",
            "POSTGRES_AGGREGATES_PASSWORD": "",
            "POSTGRES_AGGREGATES_PORT": "",
        },
        True,
    )
    def test_load_configuration_with_empty_envvars(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "",
            "QUERIDO_DIARIO_API_ROOT_PATH": "",
            "QUERIDO_DIARIO_URL_PREFIX": "",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": [""],
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": True,
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": [""],
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": [""],
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET": "",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_NAME": "",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL": "",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME": "",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL": "",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID": "",
            "CITY_DATABASE_CSV": "",
            "GAZETTE_OPENSEARCH_INDEX": "",
            "GAZETTE_CONTENT_FIELD": "",
            "GAZETTE_CONTENT_EXACT_FIELD_SUFFIX": "",
            "GAZETTE_PUBLICATION_DATE_FIELD": "",
            "GAZETTE_SCRAPED_AT_FIELD": "",
            "GAZETTE_TERRITORY_ID_FIELD": "",
            "THEMES_DATABASE_JSON": "",
            "THEMED_EXCERPT_CONTENT_FIELD": "",
            "THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX": "",
            "THEMED_EXCERPT_PUBLICATION_DATE_FIELD": "",
            "THEMED_EXCERPT_SCRAPED_AT_FIELD": "",
            "THEMED_EXCERPT_TERRITORY_ID_FIELD": "",
            "THEMED_EXCERPT_ENTITIES_FIELD": "",
            "THEMED_EXCERPT_SUBTHEMES_FIELD": "",
            "THEMED_EXCERPT_EMBEDDING_SCORE_FIELD": "",
            "THEMED_EXCERPT_TFIDF_SCORE_FIELD": "",
            "THEMED_EXCERPT_FRAGMENT_SIZE": 10000,
            "THEMED_EXCERPT_NUMBER_OF_FRAGMENTS": 1,
            "POSTGRES_COMPANIES_HOST": "",
            "POSTGRES_COMPANIES_DB": "",
            "POSTGRES_COMPANIES_USER": "",
            "POSTGRES_COMPANIES_PASSWORD": "",
            "POSTGRES_COMPANIES_PORT": "",
            "QUERIDO_DIARIO_OPENSEARCH_USER": "",
            "QUERIDO_DIARIO_OPENSEARCH_PASSWORD": "",
            "POSTGRES_AGGREGATES_HOST": "",
            "POSTGRES_AGGREGATES_DB": "",
            "POSTGRES_AGGREGATES_USER": "",
            "POSTGRES_AGGREGATES_PASSWORD": "",
            "POSTGRES_AGGREGATES_PORT": "",
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)

    @patch.dict(
        "os.environ",
        {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "0.0.0.0",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "myindex",
            "QUERIDO_DIARIO_API_ROOT_PATH": "api/",
            "QUERIDO_DIARIO_URL_PREFIX": "https://test.com",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": "localhost",
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": "True",
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": "GET,POST",
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": "X-Test-Test",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY": "dummy-api-key",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET": "dummy-api-secret",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_NAME": "Test Sender",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL": "sender@example.com",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME": "Test Recipient",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL": "recipient@example.com",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID": "12345",
            "CITY_DATABASE_CSV": "city_database.csv",
            "GAZETTE_OPENSEARCH_INDEX": "gazette_index",
            "GAZETTE_CONTENT_FIELD": "content",
            "GAZETTE_CONTENT_EXACT_FIELD_SUFFIX": "exact",
            "GAZETTE_PUBLICATION_DATE_FIELD": "publication_date",
            "GAZETTE_SCRAPED_AT_FIELD": "scraped_at",
            "GAZETTE_TERRITORY_ID_FIELD": "territory_id",
            "THEMES_DATABASE_JSON": "/path/to/themes_database.json",
            "THEMED_EXCERPT_CONTENT_FIELD": "excerpt_content",
            "THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX": "_exact",
            "THEMED_EXCERPT_PUBLICATION_DATE_FIELD": "publication_date",
            "THEMED_EXCERPT_SCRAPED_AT_FIELD": "scraped_at",
            "THEMED_EXCERPT_TERRITORY_ID_FIELD": "territory_id",
            "THEMED_EXCERPT_ENTITIES_FIELD": "entities",
            "THEMED_EXCERPT_SUBTHEMES_FIELD": "subthemes",
            "THEMED_EXCERPT_EMBEDDING_SCORE_FIELD": "embedding_score",
            "THEMED_EXCERPT_TFIDF_SCORE_FIELD": "tfidf_score",
            "THEMED_EXCERPT_FRAGMENT_SIZE": "1000",
            "THEMED_EXCERPT_NUMBER_OF_FRAGMENTS": "3",
            "POSTGRES_COMPANIES_HOST": "localhost",
            "POSTGRES_COMPANIES_DB": "companies_test",
            "POSTGRES_COMPANIES_USER": "test_user",
            "POSTGRES_COMPANIES_PASSWORD": "test_password",
            "POSTGRES_COMPANIES_PORT": "5432",
            "QUERIDO_DIARIO_OPENSEARCH_USER": "admin",
            "QUERIDO_DIARIO_OPENSEARCH_PASSWORD": "admin_password",
            "POSTGRES_AGGREGATES_HOST": "localhost",
            "POSTGRES_AGGREGATES_DB": "aggregates_test",
            "POSTGRES_AGGREGATES_USER": "test_user",
            "POSTGRES_AGGREGATES_PASSWORD": "test_password",
            "POSTGRES_AGGREGATES_PORT": "5432",
        },
        True,
    )
    def test_load_configuration_with_envvars_defined(self):
        expected_config_dict = {
            "QUERIDO_DIARIO_OPENSEARCH_HOST": "0.0.0.0",
            "QUERIDO_DIARIO_OPENSEARCH_INDEX": "myindex",
            "QUERIDO_DIARIO_API_ROOT_PATH": "api/",
            "QUERIDO_DIARIO_URL_PREFIX": "https://test.com",
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS": ["localhost"],
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS": True,
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS": ["GET", "POST"],
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS": ["X-Test-Test"],
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY": "dummy-api-key",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET": "dummy-api-secret",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_NAME": "Test Sender",
            "QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL": "sender@example.com",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME": "Test Recipient",
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL": "recipient@example.com",
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID": "12345",
            "CITY_DATABASE_CSV": "city_database.csv",
            "GAZETTE_OPENSEARCH_INDEX": "gazette_index",
            "GAZETTE_CONTENT_FIELD": "content",
            "GAZETTE_CONTENT_EXACT_FIELD_SUFFIX": "exact",
            "GAZETTE_PUBLICATION_DATE_FIELD": "publication_date",
            "GAZETTE_SCRAPED_AT_FIELD": "scraped_at",
            "GAZETTE_TERRITORY_ID_FIELD": "territory_id",
            "THEMES_DATABASE_JSON": "/path/to/themes_database.json",
            "THEMED_EXCERPT_CONTENT_FIELD": "excerpt_content",
            "THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX": "_exact",
            "THEMED_EXCERPT_PUBLICATION_DATE_FIELD": "publication_date",
            "THEMED_EXCERPT_SCRAPED_AT_FIELD": "scraped_at",
            "THEMED_EXCERPT_TERRITORY_ID_FIELD": "territory_id",
            "THEMED_EXCERPT_ENTITIES_FIELD": "entities",
            "THEMED_EXCERPT_SUBTHEMES_FIELD": "subthemes",
            "THEMED_EXCERPT_EMBEDDING_SCORE_FIELD": "embedding_score",
            "THEMED_EXCERPT_TFIDF_SCORE_FIELD": "tfidf_score",
            "THEMED_EXCERPT_FRAGMENT_SIZE": 1000,
            "THEMED_EXCERPT_NUMBER_OF_FRAGMENTS": 3,
            "POSTGRES_COMPANIES_HOST": "localhost",
            "POSTGRES_COMPANIES_DB": "companies_test",
            "POSTGRES_COMPANIES_USER": "test_user",
            "POSTGRES_COMPANIES_PASSWORD": "test_password",
            "POSTGRES_COMPANIES_PORT": "5432",
            "QUERIDO_DIARIO_OPENSEARCH_USER": "admin",
            "QUERIDO_DIARIO_OPENSEARCH_PASSWORD": "admin_password",
            "POSTGRES_AGGREGATES_HOST": "localhost",
            "POSTGRES_AGGREGATES_DB": "aggregates_test",
            "POSTGRES_AGGREGATES_USER": "test_user",
            "POSTGRES_AGGREGATES_PASSWORD": "test_password",
            "POSTGRES_AGGREGATES_PORT": "5432",
        }
        configuration = load_configuration()
        self.check_configuration_values(configuration, expected_config_dict)
