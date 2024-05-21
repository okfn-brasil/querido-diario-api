import os


VALID_BOOLEAN_TRUE_VALUES = [True, "True", "TRUE"]
VALID_BOOLEAN_FALSE_VALUES = [False, "False", "FALSE"]
VALID_BOOLEAN_VALUES = VALID_BOOLEAN_TRUE_VALUES + VALID_BOOLEAN_FALSE_VALUES


class Configuration:
    def __init__(self):
        self.host = os.environ.get("QUERIDO_DIARIO_OPENSEARCH_HOST", "")
        self.root_path = os.environ.get("QUERIDO_DIARIO_API_ROOT_PATH", "")
        self.url_prefix = os.environ.get("QUERIDO_DIARIO_URL_PREFIX", "")
        self.cors_allow_origins = Configuration._load_list(
            "QUERIDO_DIARIO_CORS_ALLOW_ORIGINS", ["*"]
        )
        self.cors_allow_credentials = Configuration._load_boolean(
            "QUERIDO_DIARIO_CORS_ALLOW_CREDENTIALS", True
        )
        self.cors_allow_methods = Configuration._load_list(
            "QUERIDO_DIARIO_CORS_ALLOW_METHODS", ["*"]
        )
        self.cors_allow_headers = Configuration._load_list(
            "QUERIDO_DIARIO_CORS_ALLOW_HEADERS", ["*"]
        )
        self.suggestion_mailjet_rest_api_key = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_KEY", ""
        )
        self.suggestion_mailjet_rest_api_secret = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_REST_API_SECRET", ""
        )
        self.suggestion_sender_name = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_SENDER_NAME", ""
        )
        self.suggestion_sender_email = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_SENDER_EMAIL", ""
        )
        self.suggestion_recipient_name = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_NAME", ""
        )
        self.suggestion_recipient_email = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_RECIPIENT_EMAIL", ""
        )
        self.suggestion_mailjet_custom_id = os.environ.get(
            "QUERIDO_DIARIO_SUGGESTION_MAILJET_CUSTOM_ID", ""
        )
        self.city_database_file = os.environ["CITY_DATABASE_CSV"]
        self.gazette_index = os.environ.get("GAZETTE_OPENSEARCH_INDEX", "")
        self.gazette_content_field = os.environ.get("GAZETTE_CONTENT_FIELD", "")
        self.gazette_content_exact_field_suffix = os.environ.get(
            "GAZETTE_CONTENT_EXACT_FIELD_SUFFIX", ""
        )
        self.gazette_publication_date_field = os.environ.get(
            "GAZETTE_PUBLICATION_DATE_FIELD", ""
        )
        self.gazette_scraped_at_field = os.environ.get("GAZETTE_SCRAPED_AT_FIELD", "")
        self.gazette_territory_id_field = os.environ.get(
            "GAZETTE_TERRITORY_ID_FIELD", ""
        )
        self.themes_database_file = os.environ["THEMES_DATABASE_JSON"]
        self.themed_excerpt_content_field = os.environ.get(
            "THEMED_EXCERPT_CONTENT_FIELD", ""
        )
        self.themed_excerpt_content_exact_field_suffix = os.environ.get(
            "THEMED_EXCERPT_CONTENT_EXACT_FIELD_SUFFIX", ""
        )
        self.themed_excerpt_publication_date_field = os.environ.get(
            "THEMED_EXCERPT_PUBLICATION_DATE_FIELD", ""
        )
        self.themed_excerpt_scraped_at_field = os.environ.get(
            "THEMED_EXCERPT_SCRAPED_AT_FIELD", ""
        )
        self.themed_excerpt_territory_id_field = os.environ.get(
            "THEMED_EXCERPT_TERRITORY_ID_FIELD", ""
        )
        self.themed_excerpt_entities_field = os.environ.get(
            "THEMED_EXCERPT_ENTITIES_FIELD", ""
        )
        self.themed_excerpt_subthemes_field = os.environ.get(
            "THEMED_EXCERPT_SUBTHEMES_FIELD", ""
        )
        self.themed_excerpt_embedding_score_field = os.environ.get(
            "THEMED_EXCERPT_EMBEDDING_SCORE_FIELD", ""
        )
        self.themed_excerpt_tfidf_score_field = os.environ.get(
            "THEMED_EXCERPT_TFIDF_SCORE_FIELD", ""
        )
        self.themed_excerpt_fragment_size = int(
            os.environ.get("THEMED_EXCERPT_FRAGMENT_SIZE", 10000)
        )
        self.themed_excerpt_number_of_fragments = int(
            os.environ.get("THEMED_EXCERPT_NUMBER_OF_FRAGMENTS", 1)
        )
        self.companies_database_host = os.environ.get("POSTGRES_HOST", "")
        self.companies_database_db = os.environ.get("POSTGRES_DB", "")
        self.companies_database_user = os.environ.get("POSTGRES_USER", "")
        self.companies_database_pass = os.environ.get("POSTGRES_PASSWORD", "")
        self.companies_database_port = os.environ.get("POSTGRES_PORT", "")
        self.opensearch_user = os.environ.get("QUERIDO_DIARIO_OPENSEARCH_USER", "")
        self.opensearch_pswd = os.environ.get("QUERIDO_DIARIO_OPENSEARCH_PASSWORD", "")
        self.aggregates_database_host = os.environ.get("POSTGRES_AGGREGATES_HOST", "")
        self.aggregates_database_db = os.environ.get("POSTGRES_AGGREGATES_DB", "")
        self.aggregates_database_user = os.environ.get("POSTGRES_AGGREGATES_USER", "")
        self.aggregates_database_pass = os.environ.get("POSTGRES_AGGREGATES_PASSWORD", "")
        self.aggregates_database_port = os.environ.get("POSTGRES_AGGREGATES_PORT", "")
    @classmethod
    def _load_list(cls, key, default=[]):
        value = os.environ.get(key, default)
        if isinstance(value, list):
            return value
        return value.split(",")

    @classmethod
    def _is_true(cls, value):
        return value in VALID_BOOLEAN_TRUE_VALUES

    @classmethod
    def _is_false(cls, value):
        return value in VALID_BOOLEAN_FALSE_VALUES

    @classmethod
    def _load_boolean(cls, key, default=False):
        value = os.environ.get(key, default)
        if cls._is_true(value):
            return True
        if cls._is_false(value):
            return False
        return default


def load_configuration():
    return Configuration()
