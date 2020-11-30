import os


class Configuration:
    def __init__(self):
        self.host = os.environ.get("QUERIDO_DIARIO_ELASTICSEARCH_HOST", "")
        self.index = os.environ.get("QUERIDO_DIARIO_ELASTICSEARCH_INDEX", "")
        self.root_path = os.environ.get("QUERIDO_DIARIO_API_ROOT_PATH", "")
        self.url_prefix = os.environ.get("QUERIDO_DIARIO_URL_PREFIX", "")


def load_configuration():
    return Configuration()
