import abc

class AggregatesDatabaseInterface(abc.ABC):
    """
    Interface to access data from aggregates.
    """

    @abc.abstractmethod
    def get_aggregate(self, territory_id: str = "", year: str = ""):
        """
        Get information about a aggregate.
        """

    @abc.abstractmethod
    def get_aggregates_from_state_and_year(self, state_code: str = "", year: str = ""):
        """
        Get information about aggregates from state and year.
        """
    
    @abc.abstractmethod
    def get_aggregates_from_territory(self, territory_id: str = "", start_year: str = "", end_year: str = ""):
        """
        Get information about all aggregates from territory, within an interval of year.
        """

class AggregatesAccessInterface(abc.ABC):
    """
    Interface to access data from aggregates.
    """

    @abc.abstractmethod
    def get_aggregate(self, territory_id: str = "", year: str = ""):
        """
        Get information about a aggregate.
        """

    @abc.abstractmethod
    def get_aggregates_from_state_and_year(self, state_code: str = "", year: str = ""):
        """
        Get information about aggregates from state and year.
        """
    
    @abc.abstractmethod
    def get_aggregates_from_territory(self, territory_id: str = "", start_year: str = "", end_year: str = ""):
        """
        Get information about all aggregates from territory, within an interval of year.
        """

class AggregatesAccess(AggregatesAccessInterface):
    _database_gateway = None

    def __init__(self, database_gateway=None):
        self._database_gateway = database_gateway

    def get_aggregate(self, territory_id: str = "", year: str = ""):
        aggregate_info = self._database_gateway.get_aggregate(territory_id, year)
        return aggregate_info
    
    def get_aggregates_from_state_and_year(self, state_code: str = "", year: str = ""):
        aggregates_info = self._database_gateway.get_aggregates_from_state_and_year(state_code, year)
        return aggregates_info
    
    def get_aggregates_from_territory(self, territory_id: str = "", start_year: str = "", end_year: str = ""):
        aggregates_info = self._database_gateway.get_aggregates_from_territory(territory_id, start_year, end_year)
        return aggregates_info
    
class Aggregates:
    """
    Item to represente a aggregate in memory inside the module
    """

    def __init__(
            self,
            territory_id,
            url_zip,
            year,
            last_updated,
            hash_info,
            file_size
    ):
        self.territory_id = territory_id
        self.url_zip = url_zip
        self.year = year
        self.last_updated = last_updated
        self.hash_info = hash_info
        self.file_size = file_size

    def __repr__(self):
        return f"Aggregates(territory_id={self.territory_id}, url_zip={self.url_zip}, year={self.year}, last_updated={self.last_updated}, hash_info={self.hash_info}, file_size={self.file_size})"
    
def create_aggregates_interface(database_gateway: AggregatesDatabaseInterface) -> AggregatesAccessInterface:
    if not isinstance(database_gateway, AggregatesDatabaseInterface):
        raise Exception(
            "Database gateway should implement the AggregatesDatabaseIntefaze interface"
        )
    return AggregatesAccess(database_gateway)