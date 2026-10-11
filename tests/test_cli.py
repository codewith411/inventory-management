from unittest.mock import Mock, patch

import cli


# -------------------------------------------------------------------
# API WRAPPER TESTS
# -------------------------------------------------------------------

def test_get_inventory():
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "id": 1,
            "product_name": "Organic Almond Milk",
            "price": 450,
            "stock": 20
        }
    ]
    mock_response.raise_for_status.return_value = None

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ) as mock_get:

        result = cli.get_inventory()

    assert len(result) == 1
    assert result[0]["product_name"] == "Organic Almond Milk"

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/inventory"
    )


def test_get_inventory_item():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "product_name": "Organic Almond Milk"
    }

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ) as mock_get:

        result = cli.get_inventory_item(1)

    assert result.status_code == 200
    assert result.json()["product_name"] == "Organic Almond Milk"

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1"
    )


def test_create_inventory_item():
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 3,
        "product_name": "Chocolate Milk",
        "price": 180,
        "stock": 25
    }

    item = {
        "product_name": "Chocolate Milk",
        "brands": "Brookside",
        "barcode": "0123456789014",
        "price": 180,
        "stock": 25,
        "ingredients_text": "Milk, cocoa, sugar"
    }

    with patch(
        "cli.requests.post",
        return_value=mock_response
    ) as mock_post:

        result = cli.create_inventory_item(item)

    assert result.status_code == 201
    assert result.json()["product_name"] == "Chocolate Milk"

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/inventory",
        json=item
    )


def test_update_inventory_item():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "price": 500,
        "stock": 30
    }

    updates = {
        "price": 500,
        "stock": 30
    }

    with patch(
        "cli.requests.patch",
        return_value=mock_response
    ) as mock_patch:

        result = cli.update_inventory_item(1, updates)

    assert result.status_code == 200
    assert result.json()["price"] == 500
    assert result.json()["stock"] == 30

    mock_patch.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/1",
        json=updates
    )


def test_delete_inventory_item():
    mock_response = Mock()
    mock_response.status_code = 204

    with patch(
        "cli.requests.delete",
        return_value=mock_response
    ) as mock_delete:

        result = cli.delete_inventory_item(2)

    assert result.status_code == 204

    mock_delete.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/2"
    )


def test_search_product_by_barcode():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "barcode": "3017624010701"
    }

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ) as mock_get:

        result = cli.search_product(
            barcode="3017624010701"
        )

    assert result.status_code == 200
    assert result.json()["product_name"] == "Nutella"

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/products/search",
        params={
            "barcode": "3017624010701"
        }
    )


def test_search_product_by_name():
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "product_name": "Coca-Cola",
            "brands": "Coca-Cola",
            "barcode": "5449000000439"
        }
    ]

    with patch(
        "cli.requests.get",
        return_value=mock_response
    ) as mock_get:

        result = cli.search_product(
            name="coca cola"
        )

    assert result.status_code == 200
    assert result.json()[0]["product_name"] == "Coca-Cola"

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/products/search",
        params={
            "name": "coca cola"
        }
    )


def test_import_product():
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 3,
        "product_name": "Nutella",
        "brands": "Ferrero",
        "barcode": "3017624010701",
        "price": 650,
        "stock": 10
    }

    product_data = {
        "barcode": "3017624010701",
        "price": 650,
        "stock": 10
    }

    with patch(
        "cli.requests.post",
        return_value=mock_response
    ) as mock_post:

        result = cli.import_product(product_data)

    assert result.status_code == 201
    assert result.json()["product_name"] == "Nutella"

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/inventory/import",
        json=product_data
    )


# -------------------------------------------------------------------
# INTERACTIVE CLI TESTS
# -------------------------------------------------------------------

def test_view_inventory(capsys):
    mock_inventory = [
        {
            "id": 1,
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "price": 450,
            "stock": 20
        }
    ]

    with patch(
        "cli.get_inventory",
        return_value=mock_inventory
    ):

        cli.view_inventory()

    captured = capsys.readouterr()

    assert "Organic Almond Milk" in captured.out
    assert "Silk" in captured.out
    assert "450" in captured.out
    assert "20" in captured.out


def test_view_item(capsys):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "0123456789012",
        "price": 450,
        "stock": 20,
        "ingredients_text": "Filtered water"
    }

    with patch(
        "builtins.input",
        return_value="1"
    ), patch(
        "cli.get_inventory_item",
        return_value=mock_response
    ):

        cli.view_item()

    captured = capsys.readouterr()

    assert "Organic Almond Milk" in captured.out
    assert "Silk" in captured.out
    assert "450" in captured.out


def test_add_item(capsys):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 3,
        "product_name": "Chocolate Milk"
    }

    user_inputs = iter([
        "Chocolate Milk",
        "Brookside",
        "0123456789014",
        "180",
        "25",
        "Milk, cocoa, sugar"
    ])

    with patch(
        "builtins.input",
        side_effect=lambda _: next(user_inputs)
    ), patch(
        "cli.create_inventory_item",
        return_value=mock_response
    ) as mock_create:

        cli.add_item()

    captured = capsys.readouterr()

    assert "Item added successfully!" in captured.out
    mock_create.assert_called_once()


def test_update_item(capsys):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "price": 500,
        "stock": 30
    }

    user_inputs = iter([
        "1",
        "500",
        "30"
    ])

    with patch(
        "builtins.input",
        side_effect=lambda _: next(user_inputs)
    ), patch(
        "cli.update_inventory_item",
        return_value=mock_response
    ) as mock_update:

        cli.update_item()

    captured = capsys.readouterr()

    assert "Item updated successfully!" in captured.out

    mock_update.assert_called_once_with(
        "1",
        {
            "price": 500.0,
            "stock": 30
        }
    )


def test_delete_item(capsys):
    mock_response = Mock()
    mock_response.status_code = 204

    with patch(
        "builtins.input",
        return_value="2"
    ), patch(
        "cli.delete_inventory_item",
        return_value=mock_response
    ) as mock_delete:

        cli.delete_item()

    captured = capsys.readouterr()

    assert "Item deleted successfully!" in captured.out

    mock_delete.assert_called_once_with("2")


def test_find_product_by_barcode(capsys):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "product_name": "Nutella",
        "brands": "Ferrero",
        "barcode": "3017624010701",
        "ingredients_text": "Sugar, palm oil, hazelnuts"
    }

    user_inputs = iter([
        "1",
        "3017624010701"
    ])

    with patch(
        "builtins.input",
        side_effect=lambda _: next(user_inputs)
    ), patch(
        "cli.search_product",
        return_value=mock_response
    ) as mock_search:

        cli.find_product()

    captured = capsys.readouterr()

    assert "Nutella" in captured.out
    assert "Ferrero" in captured.out

    mock_search.assert_called_once_with(
        barcode="3017624010701"
    )


def test_import_external_product(capsys):
    mock_response = Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 3,
        "product_name": "Nutella",
        "price": 650,
        "stock": 10
    }

    user_inputs = iter([
        "1",
        "3017624010701",
        "650",
        "10"
    ])

    with patch(
        "builtins.input",
        side_effect=lambda _: next(user_inputs)
    ), patch(
        "cli.import_product",
        return_value=mock_response
    ) as mock_import:

        cli.import_external_product()

    captured = capsys.readouterr()

    assert "Product imported successfully!" in captured.out

    mock_import.assert_called_once_with({
        "barcode": "3017624010701",
        "price": 650.0,
        "stock": 10
    })