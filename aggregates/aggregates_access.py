import abc
from typing import Optional, Dict

class AggregatesDatabaseInterface(abc.ABC):
    """
    Interface to access data from aggregates.
    """

    @abc.abstractmethod
    def get_aggregates(self, territory_id: Optional[str] = None, state_code: str = ""):
        """
        Get information about a aggregate.
        """

class AggregatesAccessInterface(abc.ABC):
    """
    Interface to access data from aggregates.
    """

    @abc.abstractmethod
    def get_aggregates(self, territory_id: Optional[str] = None, state_code: str = ""):
        """
        Get information about a aggregate.
        """

class AggregatesAccess(AggregatesAccessInterface):
    _database_gateway = None

    def __init__(self, database_gateway=None):
        self._database_gateway = database_gateway

    def get_aggregates(self, territory_id: Optional[str] = None, state_code: str = ""):
        aggregate_info = self._database_gateway.get_aggregates(territory_id, state_code)
        return aggregate_info
    
class Aggregates:
    """
    Item to represente a aggregate in memory inside the module
    """

    def __init__(
        self,
        territory_id,
        state_code,
        file_path,
        year,
        last_updated,
        hash_info,
        file_size_mb,
    ):
        self.territory_id = territory_id
        self.state_code = state_code
        self.file_path = file_path
        self.year = year
        self.last_updated = last_updated
        self.hash_info = hash_info
        self.file_size_mb = file_size_mb

    def __repr__(self):
        return f"Aggregates(territory_id={self.territory_id}, state_code={self.state_code}, file_path={self.file_path}, year={self.year}, last_updated={self.last_updated}, hash_info={self.hash_info}, file_size_mb={self.file_size_mb})"
        
def create_aggregates_interface(database_gateway: AggregatesDatabaseInterface) -> AggregatesAccessInterface:
    if not isinstance(database_gateway, AggregatesDatabaseInterface):
        raise Exception(
            "Database gateway should implement the AggregatesDatabaseInterface interface"
        )
    return AggregatesAccess(database_gateway)