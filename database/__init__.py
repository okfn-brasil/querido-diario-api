from gazettes import DatabaseInterface
from .csv import CSVDatabase


def create_database_interface() -> DatabaseInterface:
    return CSVDatabase()
