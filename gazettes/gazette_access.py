class GazetteRequest:
    """
    Object containing the data to filter gazettes
    """

    territory_id = None

    def __init__(self, territory_id=None):
        self.territory_id = territory_id


class GazetteDataGateway:
    """
    Interface to access storage keeping the gazettes files
    """

    def get_gazettes(self, territory_id=None):
        raise Exception("Not implemented. You should not be using this class")


class GazetteAccess:
    """
    Rules to interact with the gazettes
    """

    _data_gateway = None

    def __init__(self, gazette_data_gateway=None):
        self._data_gateway = gazette_data_gateway

    def get_gazettes(self, filters=None):
        territory_id = filters.territory_id if filters is not None else None
        for gazette in self._data_gateway.get_gazettes(territory_id=territory_id):
            yield gazette


class Gazette:
    """
    Item to represent a gazette in memory
    """

    territory_id = None

    def __init__(self, territory_id):
        self.territory_id = territory_id
