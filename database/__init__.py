import os

from companies import CompaniesDatabaseInterface
from gazettes import CitiesDatabaseInterface
from .csv import CSVDatabase
from .postgresql import PostgreSQLDatabase


def create_cities_database_interface() -> CitiesDatabaseInterface:
    return CSVDatabase()


def create_companies_database_interface(
    db_host, db_name, db_user, db_pass, db_port
) -> CompaniesDatabaseInterface:
    return PostgreSQLDatabase(db_host, db_name, db_user, db_pass, db_port)
