import os

import uvicorn

from api import app, set_gazette_interface
from gazettes import create_gazettes_interface
from database import create_database_data_mapper

database = os.environ["POSTGRES_DB"]
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
host = os.environ["POSTGRES_HOST"]
database_gateway = create_database_data_mapper(database, user, password, host)
gazettes_interface = create_gazettes_interface(database_gateway)
set_gazette_interface(gazettes_interface)

uvicorn.run(app, host="0.0.0.0", port=8080)
