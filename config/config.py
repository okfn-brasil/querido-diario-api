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
