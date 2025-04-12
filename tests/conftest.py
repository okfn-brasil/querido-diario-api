import pytest

from pytest import fixture
from fastapi.testclient import TestClient

from api import app, configure_api_app
from gazettes import GazetteAccessInterface
from suggestions import SuggestionSent, SuggestionServiceInterface
from companies import CompaniesAccessInterface
from aggregates import AggregatesAccessInterface
from themed_excerpts import ThemedExcerptAccessInterface
from cities import CityAccessInterface


@GazetteAccessInterface.register
class MockGazetteAccessInterface:
    pass


@CityAccessInterface.register
class MockCityAccessInterface:
    pass


@SuggestionServiceInterface.register
class MockSuggestionServiceInterface:
    pass


@CompaniesAccessInterface.register
class DummyCompaniesAccessInterface:
    pass


@AggregatesAccessInterface.register
class DummyAggregatesAccessInterface:
    pass


@ThemedExcerptAccessInterface.register
class DummyThemedExcerptAccessInterface:
    pass


@pytest.fixture
def mock_gazette_interface(mocker):
    def _create_mock(return_value=(0, [])):
        interface = MockGazetteAccessInterface()
        interface.get_gazettes = mocker.Mock(return_value=return_value)
        return interface

    return _create_mock


@pytest.fixture
def mock_city_interface(mocker):
    def _create_mock(cities_info=[], city_info=None):
        interface = MockCityAccessInterface()
        interface.get_cities = mocker.Mock(return_value=cities_info)
        interface.get_city = mocker.Mock(return_value=city_info)
        return interface

    return _create_mock


@pytest.fixture
def mock_suggestion_service_interface(mocker):
    def _create_mock(success=False, status=""):
        interface = MockSuggestionServiceInterface()
        suggestion_sent = SuggestionSent(success=success, status=status)
        interface.add_suggestion = mocker.Mock(return_value=suggestion_sent)
        return interface

    return _create_mock


@pytest.fixture
def default_mocks():
    return {
        "gazettes": MockGazetteAccessInterface(),
        "themed_excerpts": DummyThemedExcerptAccessInterface(),
        "cities": MockCityAccessInterface(),
        "suggestion_service": MockSuggestionServiceInterface(),
        "companies": DummyCompaniesAccessInterface(),
        "aggregates": DummyAggregatesAccessInterface(),
    }


@pytest.fixture
def configure_app(default_mocks):
    def _inject_mock(**kwargs):
        mocks = default_mocks.copy()
        mocks.update(kwargs)
        configure_api_app(**mocks)

    return _inject_mock


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def freeze_time(freezer):
    freezer.move_to("2025-01-01 14:50:03")
