import os

import uvicorn

from api import app, configure_api_app
from gazettes import create_gazettes_interface
from index import create_elasticsearch_data_mapper
from config import load_configuration
from database import create_database_interface

configuration = load_configuration()
datagateway = create_elasticsearch_data_mapper(configuration.host, configuration.index)
database = create_database_interface()
gazettes_interface = create_gazettes_interface(datagateway, database)
configure_api_app(gazettes_interface, configuration.root_path)

uvicorn.run(app, host="0.0.0.0", port=8080, root_path=configuration.root_path)
