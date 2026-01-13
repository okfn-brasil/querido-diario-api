"""
Test helpers and mocks for API tests.
"""

from unittest.mock import MagicMock

from gazettes import GazetteAccessInterface
from suggestions import SuggestionServiceInterface
from companies import CompaniesAccessInterface
from themed_excerpts import ThemedExcerptAccessInterface
from cities import CityAccessInterface
from aggregates import AggregatesAccessInterface


@GazetteAccessInterface.register
class MockGazetteAccessInterface:
    """Mock implementation of GazetteAccessInterface"""

    pass


@SuggestionServiceInterface.register
class MockSuggestionService:
    """Mock implementation of SuggestionServiceInterface"""

    pass


@CompaniesAccessInterface.register
class MockCompaniesAccessInterface:
    """Mock implementation of CompaniesAccessInterface"""

    pass


@ThemedExcerptAccessInterface.register
class MockThemedExcerptAccessInterface:
    """Mock implementation of ThemedExcerptAccessInterface"""

    pass


@CityAccessInterface.register
class MockCityAccessInterface:
    """Mock implementation of CityAccessInterface"""

    pass


@AggregatesAccessInterface.register
class MockAggregatesAccessInterface:
    """Mock implementation of AggregatesAccessInterface"""

    pass


def create_mock_gazette_interface(
    gazettes_return=(0, []), cities_info=[], city_info=None
):
    """
    Helper to create a mock gazette interface with common return values.

    Args:
        gazettes_return: Tuple of (total, gazettes_list)
        cities_info: List of cities
        city_info: Single city info or None

    Returns:
        MockGazetteAccessInterface instance with configured mocks
    """
    interface = MockGazetteAccessInterface()
    interface.get_gazettes = MagicMock(return_value=gazettes_return)
    interface.get_cities = MagicMock(return_value=cities_info)
    interface.get_city = MagicMock(return_value=city_info)
    return interface


def create_mock_themed_excerpt_interface(
    excerpts_return=(0, []), themes=[], subthemes=[], entities=[]
):
    """
    Helper to create a mock themed excerpt interface.

    Args:
        excerpts_return: Tuple of (total, excerpts_list)
        themes: List of themes
        subthemes: List of subthemes
        entities: List of entities

    Returns:
        MockThemedExcerptAccessInterface instance with configured mocks
    """
    interface = MockThemedExcerptAccessInterface()
    interface.get_themed_excerpts = MagicMock(return_value=excerpts_return)
    interface.get_themes = MagicMock(return_value=themes)
    interface.get_subthemes = MagicMock(return_value=subthemes)
    interface.get_entities = MagicMock(return_value=entities)
    return interface


def create_mock_city_interface(cities=[], city_info=None):
    """
    Helper to create a mock city interface.

    Args:
        cities: List of cities
        city_info: Single city info or None

    Returns:
        MockCityAccessInterface instance with configured mocks
    """
    interface = MockCityAccessInterface()
    interface.get_cities = MagicMock(return_value=cities)
    interface.get_city = MagicMock(return_value=city_info)
    return interface


def create_mock_suggestion_service():
    """Helper to create a mock suggestion service"""
    return MockSuggestionService()


def create_mock_companies_interface(companies=[]):
    """
    Helper to create a mock companies interface.

    Args:
        companies: List of companies

    Returns:
        MockCompaniesAccessInterface instance with configured mocks
    """
    interface = MockCompaniesAccessInterface()
    interface.get_companies = MagicMock(return_value=companies)
    return interface


def create_mock_aggregates_interface(aggregates=[]):
    """
    Helper to create a mock aggregates interface.

    Args:
        aggregates: List of aggregates

    Returns:
        MockAggregatesAccessInterface instance with configured mocks
    """
    interface = MockAggregatesAccessInterface()
    interface.get_aggregates = MagicMock(return_value=aggregates)
    return interface


def create_default_mocks():
    """
    Helper to create default mocks for all parameters of configure_api_app.

    Returns:
        Tuple of (gazette_mock, themed_excerpt_mock, city_mock, suggestion_mock,
                  companies_mock, aggregates_mock)
    """
    return (
        create_mock_gazette_interface(),
        create_mock_themed_excerpt_interface(),
        create_mock_city_interface(),
        create_mock_suggestion_service(),
        create_mock_companies_interface(),
        create_mock_aggregates_interface(),
    )
