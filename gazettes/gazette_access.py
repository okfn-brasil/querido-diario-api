import abc
from typing import List
from enum import Enum, unique


class GazetteRequest:
    """
    Object containing the data to filter gazettes
    """

    territory_id = None

    def __init__(
        self,
        territory_id=None,
        since=None,
        until=None,
        keywords=None,
        offset: int = 0,
        size: int = 10,
        fragment_size: int = 150,
        number_of_fragments: int = 1,
        pre_tags: List[str] = [""],
        post_tags: List[str] = [""],
        sort_by: str = "descending_date",
    ):
        self.territory_id = territory_id
        self.since = since
        self.until = until
        self.keywords = keywords
        self.offset = offset
        self.size = size
        self.fragment_size = fragment_size
        self.number_of_fragments = number_of_fragments
        self.pre_tags = pre_tags
        self.post_tags = post_tags
        self.sort_by = sort_by


class GazetteDataGateway(abc.ABC):
    """
    Interface to access storage keeping the gazettes files
    """

    @abc.abstractmethod
    def get_gazettes(
        self,
        territory_id=None,
        since=None,
        until=None,
        page: int = 0,
        size: int = 10,
        fragment_size: int = 150,
        number_of_fragments: int = 1,
        pre_tags: List[str] = [""],
        post_tags: List[str] = [""],
        sort_by: str = "descending_date",
    ):
        """
        Method to get the gazette from storage
        """


class GazetteAccessInterface(abc.ABC):
    """
    Rules to interact with the gazettes
    """

    @abc.abstractmethod
    def get_gazettes(self, filters: GazetteRequest = None):
        """
        Method to get the gazettes
        """

    @abc.abstractmethod
    def get_cities(self, citi_name: str = ""):
        """
        Method to get information about the cities
        """


class DatabaseInterface(abc.ABC):
    """
    Interface to access data from databases.
    """

    @abc.abstractmethod
    def get_cities(self, city_name: str = None):
        """
        Get the cities and their openness level.
        """


class GazetteAccess(GazetteAccessInterface):

    _index_gateway = None
    _database_gateway = None

    def __init__(self, gazette_data_gateway=None, database_gateway=None):
        self._index_gateway = gazette_data_gateway
        self._database_gateway = database_gateway

    def get_gazettes(self, filters: GazetteRequest = None):
        territory_id = filters.territory_id if filters is not None else None
        since = filters.since if filters is not None else None
        until = filters.until if filters is not None else None
        keywords = filters.keywords if filters is not None else []
        offset = filters.offset if filters is not None else 0
        size = filters.size if filters is not None else 10
        fragment_size = filters.fragment_size if filters is not None else 150
        number_of_fragments = filters.number_of_fragments if filters is not None else 1
        pre_tags = filters.pre_tags if filters is not None else [""]
        post_tags = filters.post_tags if filters is not None else [""]
        sort_by = filters.sort_by if filters is not None else "descending_date"
        total_number_gazettes, gazettes = self._index_gateway.get_gazettes(
            territory_id=territory_id,
            since=since,
            until=until,
            keywords=keywords,
            offset=offset,
            size=size,
            fragment_size=fragment_size,
            number_of_fragments=number_of_fragments,
            pre_tags=pre_tags,
            post_tags=post_tags,
            sort_by=sort_by,
        )
        return (total_number_gazettes, [vars(gazette) for gazette in gazettes])

    def get_cities(self, city_name: str = ""):
        return [vars(city) for city in self._database_gateway.get_cities(city_name)]


@unique
class OpennessLevel(str, Enum):
    ZERO = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"


class City:
    def __init__(
        self,
        name: str,
        ibge_id: str,
        uf: str,
        openness_level: OpennessLevel,
        gazettes_urls: List[str],
    ):
        self.publication_urls = gazettes_urls
        self.territory_id = ibge_id
        self.territory_name = name
        self.level = openness_level
        self.state_code = uf

    def __eq__(self, other):
        return (
            self.territory_id == other.territory_id
            and self.territory_name == other.territory_name
            and self.level == other.level
            and self.state_code == other.state_code
            and self.publication_urls == other.publication_urls
        )

    def __repr__(self):
        return f"City({self.territory_name}, {self.territory_id}, {self.level}, {self.state_code}, {self.publication_urls})"

    def __hash__(self):
        return hash(
            (self.territory_id, self.territory_name, self.state_code, self.level,)
        )


class Gazette:
    """
    Item to represent a gazette in memory inside the module
    """

    def __init__(
        self,
        territory_id,
        date,
        url,
        checksum,
        territory_name,
        state_code,
        highlight_texts,
        edition=None,
        is_extra_edition=None,
        file_raw_txt=None,
    ):
        self.territory_id = territory_id
        self.date = date
        self.url = url
        self.territory_name = territory_name
        self.state_code = state_code
        self.highlight_texts = highlight_texts
        self.edition = edition
        self.is_extra_edition = is_extra_edition
        self.checksum = checksum
        self.file_raw_txt = file_raw_txt

    def __hash__(self):
        return hash(
            (
                self.territory_id,
                self.date,
                self.url,
                self.territory_name,
                self.state_code,
                str(self.highlight_texts),
                self.edition,
                self.is_extra_edition,
                self.checksum,
                self.file_raw_txt,
            )
        )

    def __eq__(self, other):
        return (
            self.checksum == other.checksum
            and self.territory_id == other.territory_id
            and self.date == other.date
            and self.url == other.url
            and self.territory_name == other.territory_name
            and self.state_code == other.state_code
            and str(self.highlight_texts) == str(other.highlight_texts)
            and self.edition == other.edition
            and self.is_extra_edition == other.is_extra_edition
            and self.file_raw_txt == other.file_raw_txt
        )

    def __repr__(self):
        return f"Gazette({self.checksum}, {self.territory_id}, {self.date}, {self.url}, {self.territory_name}, {self.state_code}, {self.highlight_texts}, {self.edition}, {self.is_extra_edition}, {self.file_raw_txt})"


def create_gazettes_interface(
    index_gateway: GazetteDataGateway, database_gateway: DatabaseInterface
):
    if not isinstance(index_gateway, GazetteDataGateway):
        raise Exception(
            "Data gateway should implement the GazetteDataGateway interface"
        )

    if not isinstance(database_gateway, DatabaseInterface):
        raise Exception(
            "Database gateway should implement the DatabaseInterface interface"
        )
    return GazetteAccess(index_gateway, database_gateway)
