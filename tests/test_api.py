import pytest
from unittest.mock import patch

from app import app, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True

    # Reset inventory before every test
    inventory.clear()
    inventory.extend([
        {
            "id": 1,
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "barcode": "0123456789012",
            "price": 450,
            "stock": 20,
            "ingredients_text": "Filtered water, almonds, cane sugar"
        },
        {
            "id": 2,
            "product_name": "Whole Wheat Bread",
            "brands": "Nature's Own",
            "barcode": "0123456789013",
            "price": 250,
            "stock": 15,
            "ingredients_text": "Whole wheat flour, water, yeast, salt"
        }
    ])

    with app.test_client() as client:
        yield client


# -------------------------------------------------------------------
# CRUD API TESTS
# -------------------------------------------------------------------

def test_get_all_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["product_name"] == "Organic Almond Milk"


def test_get_single_inventory_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == 1
    assert data["product_name"] == "Organic Almond Milk"


def test_get_inventory_item_not_found(client):
    response = client.get("/inventory/99")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Inventory item not found"


def test_create_inventory_item(client):
    response = client.post(
        "/inventory",
        json={
            "product_name": "Chocolate Milk",
            "brands": "Brookside",
            "barcode": "0123456789014",
            "price": 180,
            "stock": 25,
            "ingredients_text": "Milk, cocoa, sugar"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 3
    assert data["product_name"] == "Chocolate Milk"
    assert data["price"] == 180
    assert data["stock"] == 25


def test_create_inventory_item_missing_data(client):
    response = client.post(
        "/inventory",
        json={}
    )

    assert response.status_code == 400


def test_update_inventory_item(client):
    response = client.patch(
        "/inventory/1",
        json={
            "price": 500,
            "stock": 30
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["price"] == 500
    assert data["stock"] == 30


def test_update_inventory_item_not_found(client):
    response = client.patch(
        "/inventory/99",
        json={
            "price": 500
        }
    )

    assert response.status_code == 404


def test_delete_inventory_item(client):
    response = client.delete("/inventory/2")

    assert response.status_code == 204

    response = client.get("/inventory/2")

    assert response.status_code == 404


def test_delete_inventory_item_not_found(client):
    response = client.delete("/inventory/99")

    assert response.status_code == 404


# -------------------------------------------------------------------
# OPENFOODFACTS SEARCH ROUTE TESTS
# -------------------------------------------------------------------

def test_search_products_by_barcode(client):
    mock_product = {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "barcode": "3017624010701",
        "ingredients_text": "Sugar, palm oil, hazelnuts"
    }

    with patch(
        "app.search_by_barcode",
        return_value=mock_product
    ) as mock_search:

        response = client.get(
            "/products/search?barcode=3017624010701"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["product_name"] == "Nutella"
    assert data["brands"] == "Ferrero"
    assert data["barcode"] == "3017624010701"

    mock_search.assert_called_once_with(
        "3017624010701"
    )


def test_search_products_by_name(client):
    mock_products = [
        {
            "product_name": "Coca-Cola Original Taste",
            "brands": "Coca-Cola",
            "barcode": "5449000054227",
            "ingredients_text": "Water, sugar, carbon dioxide"
        },
        {
            "product_name": "Coca Cola",
            "brands": "Coca-Cola",
            "barcode": "5449000000439",
            "ingredients_text": "Carbonated water, sugar"
        }
    ]

    with patch(
        "app.search_by_name",
        return_value=mock_products
    ) as mock_search:

        response = client.get(
            "/products/search?name=coca%20cola"
        )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["product_name"] == "Coca-Cola Original Taste"

    mock_search.assert_called_once_with("coca cola")


def test_search_products_missing_parameters(client):
    response = client.get("/products/search")

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Provide either barcode or name"


def test_search_products_barcode_not_found(client):
    with patch(
        "app.search_by_barcode",
        return_value=None
    ):

        response = client.get(
            "/products/search?barcode=0000000000000"
        )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Product not found"


# -------------------------------------------------------------------
# IMPORT FROM OPENFOODFACTS TESTS
# -------------------------------------------------------------------

def test_import_product_by_barcode(client):
    mock_product = {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "barcode": "3017624010701",
        "ingredients_text": "Sugar, palm oil, hazelnuts"
    }

    with patch(
        "app.search_by_barcode",
        return_value=mock_product
    ) as mock_search:

        response = client.post(
            "/inventory/import",
            json={
                "barcode": "3017624010701",
                "price": 650,
                "stock": 10
            }
        )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 3
    assert data["product_name"] == "Nutella"
    assert data["brands"] == "Ferrero"
    assert data["barcode"] == "3017624010701"
    assert data["price"] == 650
    assert data["stock"] == 10

    assert len(inventory) == 3

    mock_search.assert_called_once_with(
        "3017624010701"
    )


def test_import_product_by_name(client):
    mock_products = [
        {
            "product_name": "Coca-Cola Original Taste",
            "brands": "Coca-Cola",
            "barcode": "5449000054227",
            "ingredients_text": "Water, sugar, carbon dioxide"
        }
    ]

    with patch(
        "app.search_by_name",
        return_value=mock_products
    ) as mock_search:

        response = client.post(
            "/inventory/import",
            json={
                "name": "coca cola",
                "price": 180,
                "stock": 25
            }
        )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == 3
    assert data["product_name"] == "Coca-Cola Original Taste"
    assert data["brands"] == "Coca-Cola"
    assert data["barcode"] == "5449000054227"
    assert data["price"] == 180
    assert data["stock"] == 25

    assert len(inventory) == 3

    mock_search.assert_called_once_with("coca cola")


def test_import_product_not_found_by_barcode(client):
    with patch(
        "app.search_by_barcode",
        return_value=None
    ):

        response = client.post(
            "/inventory/import",
            json={
                "barcode": "0000000000000",
                "price": 100,
                "stock": 5
            }
        )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Product not found"

    assert len(inventory) == 2


def test_import_product_missing_search_input(client):
    response = client.post(
        "/inventory/import",
        json={
            "price": 100,
            "stock": 5
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"] == "Provide either barcode or name"

    assert len(inventory) == 2