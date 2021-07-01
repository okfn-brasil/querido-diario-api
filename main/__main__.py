import os

import uvicorn

from api import app, configure_api_app
from gazettes import create_gazettes_interface
from index import create_elasticsearch_data_mapper
from config import load_configuration
from database import create_database_interface
from suggestions import create_suggestion_service

configuration = load_configuration()
datagateway = create_elasticsearch_data_mapper(configuration.host, configuration.index)
database = create_database_interface()
gazettes_interface = create_gazettes_interface(datagateway, database)
suggestion_service = create_suggestion_service(
    suggestion_mailjet_rest_api_key=configuration.suggestion_mailjet_rest_api_key,
    suggestion_mailjet_rest_api_secret=configuration.suggestion_mailjet_rest_api_secret,
    suggestion_sender_name=configuration.suggestion_sender_name,
    suggestion_sender_email=configuration.suggestion_sender_email,
    suggestion_recipient_name=configuration.suggestion_recipient_name,
    suggestion_recipient_email=configuration.suggestion_recipient_email,
    suggestion_mailjet_custom_id=configuration.suggestion_mailjet_custom_id,
)
configure_api_app(gazettes_interface, suggestion_service, configuration.root_path)

uvicorn.run(app, host="0.0.0.0", port=8080, root_path=configuration.root_path)
