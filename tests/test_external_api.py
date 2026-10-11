import requests
from unittest.mock import patch, Mock

from external_api import search_by_barcode, search_by_name


def test_search_by_barcode_success():
    mock_response = Mock()

    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Nutella",
            "brands": "Ferrero",
            "code": "3017624010701",
            "ingredients_text": "Sugar, palm oil, hazelnuts"
        }
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "external_api.requests.get",
        return_value=mock_response
    ) as mock_get:

        result = search_by_barcode("3017624010701")

    assert result == {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "barcode": "3017624010701",
        "ingredients_text": "Sugar, palm oil, hazelnuts"
    }

    mock_get.assert_called_once()


def test_search_by_barcode_not_found():
    mock_response = Mock()

    mock_response.json.return_value = {
        "status": 0
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "external_api.requests.get",
        return_value=mock_response
    ):
        result = search_by_barcode("0000000000000")

    assert result is None


def test_search_by_barcode_request_error():
    with patch(
        "external_api.requests.get",
        side_effect=requests.RequestException("Connection error")
    ):
        result = search_by_barcode("3017624010701")

    assert result is None


def test_search_by_name_success():
    mock_response = Mock()

    mock_response.json.return_value = {
        "products": [
            {
                "product_name": "Coca-Cola Original Taste",
                "brands": "Coca-Cola",
                "code": "5449000054227",
                "ingredients_text": "Water, sugar, carbon dioxide"
            },
            {
                "product_name": "Coca Cola",
                "brands": "Coca-Cola",
                "code": "5449000000439",
                "ingredients_text": "Carbonated water, sugar"
            }
        ]
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "external_api.requests.get",
        return_value=mock_response
    ):
        result = search_by_name("coca cola")

    assert len(result) == 2

    assert result[0]["product_name"] == (
        "Coca-Cola Original Taste"
    )

    assert result[0]["brands"] == "Coca-Cola"

    assert result[0]["barcode"] == "5449000054227"


def test_search_by_name_empty():
    mock_response = Mock()

    mock_response.json.return_value = {
        "products": []
    }

    mock_response.raise_for_status.return_value = None

    with patch(
        "external_api.requests.get",
        return_value=mock_response
    ):
        result = search_by_name(
            "something-that-does-not-exist"
        )

    assert result == []


def test_search_by_name_invalid_input():
    assert search_by_name("") == []
    assert search_by_name("   ") == []