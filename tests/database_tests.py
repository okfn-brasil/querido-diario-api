import os
import unittest
from unittest import TestCase
from datetime import date, timedelta

from database import QueridoDiarioDataMapper, create_database_data_mapper
from gazettes import GazetteDataGateway, Gazette
import psycopg2


def check_if_gazettes_objects_are_equal(obj1, obj2, msg=None):
    return (
        obj1.territory_id == obj2.territory_id
        and obj1.date == obj2.date
        and obj1.url == obj2.url
    )


def get_database_name():
    return os.environ["POSTGRES_DB"]


def get_database_user():
    return os.environ["POSTGRES_USER"]


def get_database_password():
    return os.environ["POSTGRES_PASSWORD"]


def has_not_database_tests_prequisites():
    return not (
        get_database_name()
        and get_database_user()
        and get_database_password()
        and database_is_running()
    )


def database_is_running():
    try:
        conn = psycopg2.connect(
            dbname=get_database_name(),
            user=get_database_user(),
            password=get_database_password(),
            host="localhost",
        )
        conn.close()
        return True
    except Exception as e:
        print(e)
    return False


class DatabaseInterfacesValidation(TestCase):
    def test_querido_diario_data_mapper_creation(self):
        mapper = QueridoDiarioDataMapper(
            get_database_name(),
            get_database_user(),
            get_database_password(),
            "localhost",
        )

    def test_if_data_mapper_is_instance_of_right_interface(self):
        mapper = QueridoDiarioDataMapper(
            get_database_name(),
            get_database_user(),
            get_database_password(),
            "localhost",
        )
        self.assertIsInstance(
            mapper,
            GazetteDataGateway,
            msg="QueridoDiarioDataMapper should be instance of the GazetteDataGateway",
        )

    def test_create_gazettes_data_mapper_function(self):
        mapper = create_database_data_mapper(
            get_database_name(),
            get_database_user(),
            get_database_password(),
            "localhost",
        )
        self.assertIsInstance(
            mapper,
            GazetteDataGateway,
            msg="QueridoDiarioDataMapper should be instance of the GazetteDataGateway",
        )

    @unittest.expectedFailure
    def test_create_gazettes_data_mapper_function_with_invalid_arguments(self):
        create_database_data_mapper(1, 2, 3, 4)


@unittest.skipIf(has_not_database_tests_prequisites(), "Test needs a database running")
class DatabaseConnection(TestCase):
    """
    Test the database connection logic.
    """

    @unittest.expectedFailure
    def test_data_mapper_connection_with_invalid_connection_arguments(self):
        mapper = QueridoDiarioDataMapper(
            "dummy database name", "dummy user", "dummy password", "dummy host",
        )
        mapper.connect()

    def test_data_mapper_connection(self):
        mapper = QueridoDiarioDataMapper(
            get_database_name(),
            get_database_user(),
            get_database_password(),
            "localhost",
        )
        mapper.connect()


@unittest.skipIf(has_not_database_tests_prequisites(), "Test needs a database running")
class DatabaseMigrations(TestCase):
    """
    Test the database structure (e.g.table creation).
    """

    def test_data_mapper_connection_should_create_tables(self):
        mapper = QueridoDiarioDataMapper(
            get_database_name(),
            get_database_user(),
            get_database_password(),
            "localhost",
        )
        mapper.connect()

        dbconnection = psycopg2.connect(
            dbname=get_database_name(),
            user=get_database_user(),
            password=get_database_password(),
            host="localhost",
        )
        cursor = dbconnection.cursor()
        cursor.execute("SELECT to_regclass('public.gazettes');")
        self.assertEqual(
            cursor.fetchone()[0], "gazettes", msg="Cannot find the gazettes table"
        )

        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name='gazettes'"
        )
        self.assertCountEqual(
            cursor.fetchall(),
            [("id",), ("territory_id",), ("date",), ("url",)],
            msg="Gazettes table does not have the exptected columns",
        )


@unittest.skipIf(has_not_database_tests_prequisites(), "Test needs a database running")
class DatabaseTest(TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(Gazette, check_if_gazettes_objects_are_equal)
        self._mapper = QueridoDiarioDataMapper(
            get_database_name(),
            get_database_user(),
            get_database_password(),
            "localhost",
        )
        self._mapper.connect()
        self._dbconnection = psycopg2.connect(
            dbname=get_database_name(),
            user=get_database_user(),
            password=get_database_password(),
            host="localhost",
        )
        cursor = self._dbconnection.cursor()
        cursor.execute("DELETE FROM gazettes;")
        self._gazettes_data = [
            (1, "4205902", date.today(), "https://queridodiario.ok.org.br/"),
            (2, "4202909", date.today(), "https://queridodiario.ok.org.br/"),
            (
                3,
                "4202910",
                date.today() - timedelta(days=1),
                "https://queridodiario.ok.org.br/",
            ),
            (
                4,
                "4202910",
                date.today() + timedelta(days=1),
                "https://queridodiario.ok.org.br/",
            ),
            (5, "4202910", date.today(), "https://queridodiario.ok.org.br/"),
            (
                6,
                "4202910",
                date.today() - timedelta(days=2),
                "https://queridodiario.ok.org.br/",
            ),
            (
                7,
                "4205902",
                date.today() - timedelta(days=1),
                "https://queridodiario.ok.org.br/",
            ),
            (
                8,
                "4202909",
                date.today() + timedelta(days=1),
                "https://queridodiario.ok.org.br/",
            ),
            (
                9,
                "4205902",
                date.today() + timedelta(days=1),
                "https://queridodiario.ok.org.br/",
            ),
        ]
        cursor = self._dbconnection.cursor()
        for data in self._gazettes_data:
            cursor.execute(
                "INSERT INTO gazettes (id, territory_id, date, url) VALUES (%s, %s, %s, %s)",
                data,
            )

        self._dbconnection.commit()
        cursor.close()

    def tearDown(self):
        self._dbconnection.close()
        self._mapper.close()

    def test_get_gazettes_should_return_gazzete_objects(self):
        for gazette in self._mapper.get_gazettes():
            self.assertIsInstance(
                gazette,
                Gazette,
                msg="get_gazette function should return Gazette objects",
            )

    def test_data_mapper_get_gazettes_from_database(self):
        gazettes_expected = [
            Gazette(data[1], data[2], data[3]) for data in self._gazettes_data
        ]
        gazettes_found = list(self._mapper.get_gazettes())
        self.assertEqual(len(gazettes_found), len(gazettes_expected))
        for found, expected in zip(gazettes_found, gazettes_expected):
            self.assertEqual(found, expected)

    def test_data_mapper_get_gazettes_from_database_by_territory_id(self):
        gazettes_expected = [
            Gazette(data[1], data[2], data[3])
            for data in self._gazettes_data
            if data[1] == "4205902"
        ]
        gazettes_found = list(self._mapper.get_gazettes(territory_id="4205902"))
        self.assertEqual(len(gazettes_expected), len(gazettes_found))
        self.assertEqual(gazettes_found[0], gazettes_expected[0])

        gazettes_expected = [
            Gazette(data[1], data[2], data[3])
            for data in self._gazettes_data
            if data[1] == "4202909"
        ]
        gazettes_found = list(self._mapper.get_gazettes(territory_id="4202909"))
        self.assertEqual(len(gazettes_expected), len(gazettes_found))
        self.assertEqual(gazettes_found[0], gazettes_expected[0])

    def test_data_mapper_get_gazettes_from_database_since_date(self):
        gazettes_expected = [
            Gazette(data[1], data[2], data[3])
            for data in self._gazettes_data
            if data[2] >= date.today()
        ]
        gazettes_found = list(self._mapper.get_gazettes(since=date.today()))
        self.assertEqual(len(gazettes_expected), len(gazettes_found))

    def test_data_mapper_get_gazettes_from_database_until_date(self):
        gazettes_expected = [
            Gazette(data[1], data[2], data[3])
            for data in self._gazettes_data
            if data[2] <= date.today()
        ]
        gazettes_found = list(self._mapper.get_gazettes(until=date.today()))
        self.assertEqual(len(gazettes_expected), len(gazettes_found))

    def test_data_mapper_get_gazettes_from_database_with_since_and_until_date(self):
        gazettes_expected = [
            Gazette(data[1], data[2], data[3])
            for data in self._gazettes_data
            if (
                data[2] <= date.today()
                and (data[2] >= (date.today() - timedelta(days=3)))
            )
        ]
        gazettes_found = list(self._mapper.get_gazettes(until=date.today()))
        self.assertEqual(len(gazettes_expected), len(gazettes_found))

    def test_data_mapper_get_gazettes_from_database_by_territory_within_data_range(
        self,
    ):
        gazettes_expected = [
            Gazette(data[1], data[2], data[3])
            for data in self._gazettes_data
            if (
                data[2] <= date.today()
                and (data[2] >= (date.today() - timedelta(days=2)))
                and (data[1] == "4205902")
            )
        ]
        gazettes_found = list(
            self._mapper.get_gazettes(
                territory_id="4205902",
                until=date.today(),
                since=(date.today() - timedelta(days=1)),
            )
        )
        self.assertEqual(len(gazettes_expected), len(gazettes_found))
