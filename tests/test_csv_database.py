from unittest import TestCase, expectedFailure
from unittest.mock import patch, MagicMock
import os
import unittest
from tempfile import NamedTemporaryFile
import csv

from cities import create_cities_data_gateway
from cities.city_access import CitySearchResult, OpennessLevel


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
            {
                "city_name": "São Paulo de Olivença",
                "ibge_id": "1237",
                "uf": "AM",
                "openness_level": 0,
                "gazettes_urls":[]
            },
            {
                "city_name": "São Paulo do Potengi",
                "ibge_id": "1238",
                "uf": "RN",
                "openness_level": 0,
                "gazettes_urls": []
            },
            {
                "city_name": "São Paulo",
                "ibge_id": "1239",
                "uf": "SP",
                "openness_level": 1,
                "gazettes_urls": [
                    "https://somewebsite.org"
                ]
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


    def create_database(self):
        city_database_file = os.environ.get('CITY_DATABASE_CSV')
        database = create_cities_data_gateway(city_database_file)
        return database


    def test_get_file_name_from_envvar(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()
            self.assertEqual(self.database_file, database._database_file)


    @expectedFailure
    def test_create_csv_database_without_envvar_with_file_path(self):
        with patch.dict(os.environ, {"CITY_DATABASE_CSV": "/path/does/not/exists"}):
            database = self.create_database()

        with patch.dict(os.environ, {"CITY_DATABASE_CSV": ""}):
            database = self.create_database()

        with patch.dict(os.environ, {}):
            database = self.create_database()


    def test_get_one_city_by_name(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()

            city = database.get_cities("pira", [])

            expected_cites = CitySearchResult(
                name="Piraporinha",
                ibge_id="1234",
                uf="SC",
                openness_level=OpennessLevel.TWO,
                gazettes_urls=['https://somewebsite.org']
            )

            self.assertCountEqual([expected_cites], city)


    def test_get_one_city_by_name_and_by_level(self):
            with patch.dict(
                os.environ, {"CITY_DATABASE_CSV": self.database_file}
            ):
                database = self.create_database()

                levels = ["2"]

                city = database.get_cities("pira", levels)

                expected_cites = CitySearchResult(
                    name="Piraporinha",
                    ibge_id="1234",
                    uf="SC",
                    openness_level=OpennessLevel.TWO,
                    gazettes_urls=['https://somewebsite.org']
                )

                self.assertCountEqual([expected_cites], city)


    def test_get_one_city_by_name_by_multiple_levels(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()

            levels = ["0","1","2"]
            city = database.get_cities("pira", [])

            expected_city = CitySearchResult(
                name="Piraporinha",
                ibge_id="1234",
                uf="SC",
                openness_level=OpennessLevel.TWO,
                gazettes_urls=['https://somewebsite.org']
            )

            self.assertCountEqual([expected_city], city)


    def test_get_multiple_cities(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()

            levels = []
            cities = database.get_cities("taquarinha",levels)

            expected_cities = [
                CitySearchResult(
                    "Taquarinha Do Norte",
                    "1235",
                    "RN",
                    OpennessLevel.ONE,
                    ["https://somewebsite.org", "https://anotherwebsite.org"],
                ),

                CitySearchResult(
                    "Taquarinha Do Sul",
                    "1236",
                    "RS",
                    OpennessLevel.THREE,
                    ["https://somewebsite.org", "https://anotherwebsite.org"],
                ),
            ]

            self.assertCountEqual(expected_cities, cities)


    def test_get_one_city_by_invalid_level(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()

            levels = ["2"]
            cities = database.get_cities("São Paulo",levels)

            expected_cities = []

            self.assertCountEqual(expected_cities, cities)


    def test_get_multiple_cities_with_unique_level(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()

            levels = ["0"]
            cities = database.get_cities("São Paulo",levels)

            expected_cities = [
                CitySearchResult(
                    "São Paulo de Olivença",
                    "1237",
                    "AM",
                    OpennessLevel.ZERO,
                    None,
                ),

                CitySearchResult(
                    "São Paulo do Potengi",
                    "1238",
                    "RN",
                    OpennessLevel.ZERO,
                    None,
                ),
            ]

            self.assertCountEqual(expected_cities, cities)


    def test_get_one_city_by_ibge_id(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            expected_city = CitySearchResult(
                "Piraporinha",
                "1234",
                "SC",
                OpennessLevel.TWO,
                ["https://somewebsite.org"],
            )

            database = self.create_database()
            city = database.get_city("1234")
            self.assertEqual(expected_city, city)


    def test_get_none_by_invalid_ibge_id(self):
        with patch.dict(
            os.environ, {"CITY_DATABASE_CSV": self.database_file}
        ):
            database = self.create_database()
            city = database.get_city("invalid_id")
            self.assertEqual(None, city)
