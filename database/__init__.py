from companies import CompaniesDatabaseInterface
from aggregates import AggregatesDatabaseInterface

from .postgresql import PostgreSQLDatabaseCompanies, PostgreSQLDatabaseAggregates


def create_companies_database_interface(
    db_host, db_name, db_user, db_pass, db_port
) -> CompaniesDatabaseInterface:
    return PostgreSQLDatabaseCompanies(db_host, db_name, db_user, db_pass, db_port)


def create_aggregates_database_interface(
    db_host, db_name, db_user, db_pass, db_port
) -> AggregatesDatabaseInterface:
    return PostgreSQLDatabaseAggregates(db_host, db_name, db_user, db_pass, db_port)
