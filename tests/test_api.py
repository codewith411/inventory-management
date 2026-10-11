import pytest

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