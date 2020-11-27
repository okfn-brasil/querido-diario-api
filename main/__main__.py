import os

import uvicorn

from api import app, set_gazette_interface
from gazettes import create_gazettes_interface
from database import create_elasticsearch_data_mapper

host = os.environ["QUERIDO_DIARIO_ELASTICSEARCH_HOST"]
index = os.environ["QUERIDO_DIARIO_ELASTICSEARCH_INDEX"]
root_path = os.environ.get("QUERIDO_DIARIO_API_ROOT_PATH", "")

def get_url_prefix():
    return os.environ.get("QUERIDO_DIARIO_URL_PREFIX", "")


datagateway = create_elasticsearch_data_mapper(host, index)
gazettes_interface = create_gazettes_interface(datagateway, get_url_prefix())
set_gazette_interface(gazettes_interface)

uvicorn.run(app, host="0.0.0.0", port=8080, root_path=root_path)
