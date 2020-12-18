import abc


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
        page: int = 0,
        page_size: int = 10,
    ):
        self.territory_id = territory_id
        self.since = since
        self.until = until
        self.keywords = keywords
        self.page = page
        self.page_size = page_size


class GazetteDataGateway(abc.ABC):
    """
    Interface to access storage keeping the gazettes files
    """

    @abc.abstractmethod
    def get_gazettes(
        self, territory_id=None, since=None, until=None, page: int = 0, size: int = 10
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


class GazetteAccess(GazetteAccessInterface):

    _data_gateway = None

    def __init__(self, gazette_data_gateway=None):
        self._data_gateway = gazette_data_gateway

    def get_gazettes(self, filters: GazetteRequest = None):
        territory_id = filters.territory_id if filters is not None else None
        since = filters.since if filters is not None else None
        until = filters.until if filters is not None else None
        keywords = filters.keywords if filters is not None else []
        page = filters.page if filters is not None else 1
        page_size = filters.page_size if filters is not None else 10
        for gazette in self._data_gateway.get_gazettes(
            territory_id=territory_id,
            since=since,
            until=until,
            keywords=keywords,
            page=page,
            page_size=page_size,
        ):
            yield vars(gazette)


class Gazette:
    """
    Item to represent a gazette in memory inside the module
    """

    territory_id = None
    date = None
    url = None

    def __init__(self, territory_id, date, url):
        self.territory_id = territory_id
        self.date = date
        self.url = url

    def __hash__(self):
        return hash((self.territory_id, self.date, self.url))

    def __eq__(self, other):
        return (
            self.territory_id == other.territory_id
            and self.date == other.date
            and self.url == other.url
        )


def create_gazettes_interface(data_gateway: GazetteDataGateway):
    if not isinstance(data_gateway, GazetteDataGateway):
        raise Exception(
            "Data gateway should implement the GazetteDataGateway interface"
        )
    return GazetteAccess(data_gateway)
