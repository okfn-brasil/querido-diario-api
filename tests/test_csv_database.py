from unittest import TestCase, expectedFailure
from unittest.mock import patch, MagicMock
import os
import unittest
from tempfile import NamedTemporaryFile
import csv

from gazettes import GazetteDataGateway, Gazette, OpennessLevel, City
from database.csv import CSVDatabase


class CSVDatabaseTests(TestCase):
    def setUp(self):
        self.fake_database_data = [
            {
                "city_name": "Piraporinha",
                "ibge_id": "1234",
                "uf": "SC",
                "openness_level": 2,
                "gazettes_urls": ["https://somewebsite.org"],
            },
            {
                "city_name": "Taquarinha Do Norte",
                "ibge_id": "1235",
                "uf": "RN",
                "openness_level": 1,
                "gazettes_urls": [
                    "https://somewebsite.org",
                    "https://anotherwebsite.org",
                ],
            },
            {
                "city_name": "Taquarinha Do Sul",
                "ibge_id": "1236",
                "uf": "RS",
                "openness_level": 3,
                "gazettes_urls": [
                    "https://somewebsite.org",
                    "https://anotherwebsite.org",
                ],
            },
        ]
        self.database_file = NamedTemporaryFile(delete=False).name
        self.create_fake_csv_database_file(self.fake_database_data)

    def tearDown(self):
        if self.database_file is not None:
            os.remove(self.database_file)

    def create_fake_csv_database_file(self, data):
        with open(self.database_file, "w", newline="") as csvfile:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                row["gazettes_urls"] = ",".join(row["gazettes_urls"])
                writer.writerow(row)

    def test_get_file_name_from_envvar(self):
        with patch.dict(
            os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": self.database_file}
        ):
            database = CSVDatabase()
            self.assertEqual(self.database_file, database.database_file)

    @expectedFailure
    def test_create_csv_database_without_envvar_with_file_path(self):
        with patch.dict(
            os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": "/path/does/not/exists"}
        ):
            database = CSVDatabase()
        with patch.dict(os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": ""}):
            database = CSVDatabase()
        with patch.dict(os.environ, {}):
            database = CSVDatabase()

    def test_get_one_city_by_name(self):
        with patch.dict(
            os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": self.database_file}
        ):
            database = CSVDatabase()
            city = database.get_cities("pira")
            expected_city = City(
                "Piraporinha",
                "1234",
                "SC",
                OpennessLevel("2"),
                ["https://somewebsite.org"],
            )
            self.assertCountEqual([expected_city], city)

    def test_get_multiple_cities(self):
        with patch.dict(
            os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": self.database_file}
        ):
            database = CSVDatabase()
            cities = database.get_cities("taquarinha")
            expected_cities = [
                City(
                    "Taquarinha Do Norte",
                    "1235",
                    "RN",
                    OpennessLevel("1"),
                    ["https://somewebsite.org", "https://anotherwebsite.org"],
                ),
                City(
                    "Taquarinha Do Sul",
                    "1236",
                    "RS",
                    OpennessLevel("3"),
                    ["https://somewebsite.org", "https://anotherwebsite.org"],
                ),
            ]
            self.assertCountEqual(expected_cities, cities)

    def test_get_one_city_by_territory_id(self):
        with patch.dict(
            os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": self.database_file}
        ):
            database = CSVDatabase()
            city = database.get_city("1234")
            expected_city = City(
                "Piraporinha",
                "1234",
                "SC",
                OpennessLevel("2"),
                ["https://somewebsite.org"],
            )
            self.assertEqual(expected_city, city)

    def test_get_none_by_invalid_territory_id(self):
        with patch.dict(
            os.environ, {"QUERIDO_DIARIO_DATABASE_CSV": self.database_file}
        ):
            database = CSVDatabase()
            city = database.get_city("invalid_id")
            self.assertEqual(None, city)
