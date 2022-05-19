import os


VALID_BOOLEAN_TRUE_VALUES = [True, "True", "TRUE"]
VALID_BOOLEAN_FALSE_VALUES = [False, "False", "FALSE"]
VALID_BOOLEAN_VALUES = VALID_BOOLEAN_TRUE_VALUES + VALID_BOOLEAN_FALSE_VALUES


class Configuration:
    def __init__(self):
        self.host = os.environ.get("QUERIDO_DIARIO_ELASTICSEARCH_HOST", "")
        self.index = os.environ.get("QUERIDO_DIARIO_ELASTICSEARCH_INDEX", "")
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
        self.companies_database_host = os.environ.get("POSTGRES_HOST", "")
        self.companies_database_db = os.environ.get("POSTGRES_DB", "")
        self.companies_database_user = os.environ.get("POSTGRES_USER", "")
        self.companies_database_pass = os.environ.get("POSTGRES_PASSWORD", "")
        self.companies_database_port = os.environ.get("POSTGRES_PORT", "")

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
