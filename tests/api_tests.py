from datetime import date
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
import pytest

from api import app, set_gazette_interface
from gazettes import GazetteAccessInterface, GazetteRequest


@GazetteAccessInterface.register
class MockGazetteAccessInterface:
    pass


def create_mock_gazette_interface(return_value=None):
    interface = MockGazetteAccessInterface()
    interface.get_gazettes = MagicMock(return_value=return_value)
    return interface


def test_api_should_fail_when_try_to_set_any_object_as_gazettes_interface():
    with pytest.raises(Exception):
        set_gazette_interface(MagicMock())


def test_api_should_not_fail_when_try_to_set_any_object_as_gazettes_interface():
    set_gazette_interface(MockGazetteAccessInterface())


def test_gazettes_endpoint_should_accept_territory_id():
    set_gazette_interface(create_mock_gazette_interface())
    client = TestClient(app)
    response = client.get("/gazettes/4205902")
    assert response.status_code == 200


def test_get_gazettes_without_territory_id_should_fail():
    set_gazette_interface(MockGazetteAccessInterface())
    client = TestClient(app)
    response = client.get("/gazettes/")
    assert response.status_code == 404


def test_get_gazettes_should_request_gazettes_to_interface_object():
    interface = create_mock_gazette_interface()
    set_gazette_interface(interface)
    client = TestClient(app)
    response = client.get("/gazettes/4205902")
    assert response.status_code == 200
    interface.get_gazettes.assert_called_once()


def test_get_gazettes_should_return_json_with_items():
    today = date.today()
    interface = create_mock_gazette_interface(
        [
            {
                "territory_id": "4205902",
                "date": today,
                "url": "https://queridodiario.ok.org.br/",
            }
        ]
    )
    set_gazette_interface(interface)
    client = TestClient(app)
    response = client.get("/gazettes/4205902")
    interface.get_gazettes.assert_called_once()
    assert interface.get_gazettes.call_args.args[0].territory_id == "4205902"
    assert response.status_code == 200
    assert response.json() == [
        {
            "territory_id": "4205902",
            "date": today.strftime("%Y-%m-%d"),
            "url": "https://queridodiario.ok.org.br/",
        }
    ]


def test_get_gazettes_should_return_empty_list_when_no_gazettes_is_found():
    today = date.today()
    interface = create_mock_gazette_interface()
    set_gazette_interface(interface)
    client = TestClient(app)
    response = client.get("/gazettes/4205902")
    interface.get_gazettes.assert_called_once()
    assert interface.get_gazettes.call_args.args[0].territory_id == "4205902"
    assert response.status_code == 200
    assert response.json() == []
