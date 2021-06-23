import csv
import os

from gazettes import DatabaseInterface, City, OpennessLevel


class CSVDatabase(DatabaseInterface):
    """
    A simple database interface implementation to allow load data from file.
    This is not intent to be used in production. But it can be used to avoid blocking
    other code changes for now.
    """

    def __init__(self):
        self.database_file = os.environ["QUERIDO_DIARIO_DATABASE_CSV"]
        if not os.path.exists(self.database_file):
            raise Exception("Missing databasefile")

    def get_cities(self, city_name: str = None):
        results = []
        with open(self.database_file) as database:
            reader = csv.DictReader(database)
            for row in reader:
                if city_name.lower() in row["city_name"].lower():
                    city = City(
                        row["city_name"],
                        row["ibge_id"],
                        row["uf"],
                        OpennessLevel(row["openness_level"]),
                        self._split_urls(row["gazettes_urls"]),
                    )
                    results.append(city)
        return results

    def get_city(self, territory_id: str = None):
        with open(self.database_file) as database:
            reader = csv.DictReader(database)
            for row in reader:
                if territory_id == row["ibge_id"]:
                    city = City(
                        row["city_name"],
                        row["ibge_id"],
                        row["uf"],
                        OpennessLevel(row["openness_level"]),
                        self._split_urls(row["gazettes_urls"]),
                    )
                    return city

    def _split_urls(self, concatenated_urls: str = None):
        urls = concatenated_urls.strip().split(",")
        if len(urls) == 1 and len(urls[0]) == 0:
            urls = None
        return urls
