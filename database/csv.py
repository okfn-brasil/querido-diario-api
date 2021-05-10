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

    def get_cities(self, city_name: str = None):
        results = []
        with open(self.database_file) as database:
            reader = csv.DictReader(database)
            for row in reader:
                if city_name.lower() in row["city_name"].lower():
                    urls = row["gazettes_urls"].split(",")
                    city = City(
                        row["city_name"],
                        row["ibge_id"],
                        row["uf_name"],
                        row["uf_short_name"],
                        OpennessLevel(int(row["openness_level"])),
                        urls,
                    )
                    results.append(city)
        return results
