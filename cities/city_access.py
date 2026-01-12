import abc
import csv
import os
from typing import List, Union
from enum import Enum, unique


@unique
class OpennessLevel(str, Enum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"


class CitySearchResult:
    def __init__(
        self,
        name: str,
        ibge_id: str,
        uf: str,
        openness_level: OpennessLevel,
        gazettes_urls: List[str],
        availability_date: str,
    ):
        self.publication_urls = gazettes_urls
        self.territory_id = ibge_id
        self.territory_name = name
        self.level = openness_level
        self.state_code = uf
        self.availability_date = availability_date

    def __eq__(self, other):
        return (
            self.territory_id == other.territory_id
            and self.territory_name == other.territory_name
            and self.level == other.level
            and self.state_code == other.state_code
            and self.publication_urls == other.publication_urls
            and self.availability_date == other.availability_date
        )

    def __repr__(self):
        return f"CitySearchResult({self.territory_name}, {self.territory_id}, {self.level}, {self.state_code}, {self.publication_urls}, {self.availability_date})"

    def __hash__(self):
        return hash(
            (
                self.territory_id,
                self.territory_name,
                self.state_code,
                self.level,
                self.availability_date,
            )
        )


class CityDataGateway(abc.ABC):
    """
    Interface to access cities' data from databases
    """

    @abc.abstractmethod
    def get_cities(self, city_name: str, levels: List[str]):
        """
        Method to get information about the cities from storage
        """

    @abc.abstractmethod
    def get_city(self, territory_id: str):
        """
        Method to get information about a specific city from storage
        """


class CityAccessInterface(abc.ABC):
    """
    Rules to interact with cities
    """

    @abc.abstractmethod
    def get_cities(self, city_name: str, levels: List[str]):
        """
        Method to get information about the cities
        """

    @abc.abstractmethod
    def get_city(self, territory_id: str):
        """
        Method to get information about a specific city
        """


class CitiesCSVDatabaseGateway(CityDataGateway):
    """
    A simple database interface implementation to allow load data from file.
    This is not intent to be used in production. But it can be used to avoid blocking
    other code changes for now.
    """

    def __init__(self, database_file: str):
        self._database_file = database_file
        if not os.path.exists(self._database_file):
            raise Exception("Missing databasefile")

    def get_cities(self, city_name: str, levels: List[str]):
        results = []
        with open(self._database_file) as database:
            reader = csv.DictReader(database)
            for row in reader:
                if city_name.lower() not in row["city_name"].lower():
                    continue

                if levels == [""] or levels == [] or row["openness_level"] in levels:
                    city = CitySearchResult(
                        row["city_name"],
                        row["ibge_id"],
                        row["uf"],
                        OpennessLevel(row["openness_level"]),
                        self._split_urls(row["gazettes_urls"]),
                        row["availability_date"],
                    )
                    results.append(city)
        return results

    def get_city(self, territory_id: str):
        with open(self._database_file) as database:
            reader = csv.DictReader(database)
            for row in reader:
                if territory_id == row["ibge_id"]:
                    city = CitySearchResult(
                        row["city_name"],
                        row["ibge_id"],
                        row["uf"],
                        OpennessLevel(row["openness_level"]),
                        self._split_urls(row["gazettes_urls"]),
                        row["availability_date"],
                    )
                    return city

    def _split_urls(self, concatenated_urls: str) -> Union[List[str], None]:
        urls = concatenated_urls.strip().split(",")
        if len(urls) == 1 and len(urls[0]) == 0:
            urls = None
        return urls


class CityAccess(CityAccessInterface):
    def __init__(self, data_gateway: CityDataGateway):
        self._data_gateway = data_gateway

    def get_cities(self, city_name: str, levels: List[str]):
        return [vars(city) for city in self._data_gateway.get_cities(city_name, levels)]

    def get_city(self, territory_id: str):
        city = self._data_gateway.get_city(territory_id)
        return vars(city) if city is not None else None


def create_cities_data_gateway(city_database_file: str) -> CityDataGateway:
    return CitiesCSVDatabaseGateway(city_database_file)


def create_cities_interface(data_gateway: CityDataGateway,) -> CityAccessInterface:
    if not isinstance(data_gateway, CityDataGateway):
        raise Exception("Data gateway should implement the CityDataGateway interface")

    return CityAccess(data_gateway)
