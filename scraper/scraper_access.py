import abc
from datetime import date, datetime
from typing import Dict, List, Optional


class InvalidTerritoryIDException(Exception):
    pass


class ScraperDatabaseInterface(abc.ABC):
    """
    Interface to access the data used by the scrapers.
    """

    @abc.abstractmethod
    def get_enabled_spiders(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Get the list of enabled spiders.
        """

    @abc.abstractmethod
    def insert_gazette(self, gazette: Dict) -> Optional[int]:
        """
        Insert a scraped gazette. Returns the new gazette ID or None if the
        gazette already exists (duplicate).
        """

    @abc.abstractmethod
    def insert_job_stats(
        self, spider_name: str, job_id: Optional[str], stats: Dict
    ) -> int:
        """
        Insert the stats of a finished scraping job. Returns the new job stats ID.
        """

    @abc.abstractmethod
    def get_job_stats(
        self, spider: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get the stats of scraping jobs.
        """


class ScraperAccessInterface(abc.ABC):
    """
    Interface to access data used by the scrapers.
    """

    @abc.abstractmethod
    def get_enabled_spiders(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Get the list of enabled spiders.
        """

    @abc.abstractmethod
    def create_gazette(self, gazette: Dict) -> Optional[int]:
        """
        Persist a scraped gazette. Returns the new gazette ID or None if the
        gazette already exists (duplicate).
        """

    @abc.abstractmethod
    def create_job_stats(
        self, spider_name: str, job_id: Optional[str], stats: Dict
    ) -> int:
        """
        Persist the stats of a finished scraping job. Returns the new job stats ID.
        """

    @abc.abstractmethod
    def get_job_stats(
        self, spider: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get the stats of scraping jobs.
        """

    @abc.abstractmethod
    def sync_spiders(self, territory_spider_map: List[tuple]) -> int:
        """
        Register new or modified spiders and their territory mapping.
        Returns the number of spiders processed.
        """


class ScraperAccess(ScraperAccessInterface):
    _database_gateway = None

    def __init__(self, database_gateway=None):
        self._database_gateway = database_gateway

    def get_enabled_spiders(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Dict]:
        return self._database_gateway.get_enabled_spiders(start_date, end_date)

    def create_gazette(self, gazette: Dict) -> Optional[int]:
        return self._database_gateway.insert_gazette(gazette)

    def create_job_stats(
        self, spider_name: str, job_id: Optional[str], stats: Dict
    ) -> int:
        return self._database_gateway.insert_job_stats(spider_name, job_id, stats)

    def get_job_stats(
        self, spider: Optional[str] = None, since: Optional[datetime] = None
    ) -> List[Dict]:
        return self._database_gateway.get_job_stats(spider, since)

    def sync_spiders(self, territory_spider_map: List[tuple]) -> int:
        return self._database_gateway.sync_spiders(territory_spider_map)


def create_scraper_interface(
    database_gateway: ScraperDatabaseInterface,
) -> ScraperAccessInterface:
    if not isinstance(database_gateway, ScraperDatabaseInterface):
        raise Exception(
            "Database gateway should implement the ScraperDatabaseInterface interface"
        )
    return ScraperAccess(database_gateway)
