import abc


class GazetteRequest:
    """
    Object containing the data to filter gazettes
    """

    territory_id = None

    def __init__(self, territory_id=None, since=None, until=None):
        self.territory_id = territory_id
        self.since = since
        self.until = until


class GazetteDataGateway(abc.ABC):
    """
    Interface to access storage keeping the gazettes files
    """

    @abc.abstractmethod
    def get_gazettes(self, territory_id=None, since=None, until=None):
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
        for gazette in self._data_gateway.get_gazettes(
            territory_id=territory_id, since=since, until=until
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


def create_gazettes_interface(data_gateway: GazetteDataGateway):
    if not isinstance(data_gateway, GazetteDataGateway):
        raise Exception(
            "Data gateway should implement the GazetteDataGateway interface"
        )
    return GazetteAccess(data_gateway)
