from flask import Flask, jsonify, request

from external_api import search_by_barcode, search_by_name
app = Flask(__name__)


# Simulated inventory database
inventory = [
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
]


# GET /inventory
# Return all inventory items
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


# GET /inventory/<id>
# Return one inventory item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    return jsonify(item), 200


# POST /inventory
# Add a new inventory item
@app.route("/inventory", methods=["POST"])
def create_inventory_item():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = [
        "product_name",
        "price",
        "stock"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required"
            }), 400

    new_id = max(
        (item["id"] for item in inventory),
        default=0
    ) + 1

    new_item = {
        "id": new_id,
        "product_name": data["product_name"],
        "brands": data.get("brands", ""),
        "barcode": data.get("barcode", ""),
        "price": data["price"],
        "stock": data["stock"],
        "ingredients_text": data.get("ingredients_text", "")
    }

    inventory.append(new_item)

    return jsonify(new_item), 201


# PATCH /inventory/<id>
# Update an inventory item
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_inventory_item(item_id):
    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    allowed_fields = [
        "product_name",
        "brands",
        "barcode",
        "price",
        "stock",
        "ingredients_text"
    ]

    for field in allowed_fields:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200


# DELETE /inventory/<id>
# Delete an inventory item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory_item(item_id):
    item = next(
        (item for item in inventory if item["id"] == item_id),
        None
    )

    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    inventory.remove(item)

    return "", 204

@app.route("/products/search", methods=["GET"])
def search_products():
    """Search OpenFoodFacts by barcode or product name."""

    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        product = search_by_barcode(barcode)

        if product is None:
            return jsonify({"error": "Product not found"}), 404

        return jsonify(product), 200

    if name:
        products = search_by_name(name)
        return jsonify(products), 200

    return jsonify({
        "error": "Provide either barcode or name"
    }), 400


@app.route("/inventory/import", methods=["POST"])
def import_product():
    """Find a product on OpenFoodFacts and add it to inventory."""

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    barcode = data.get("barcode")
    name = data.get("name")

    if not barcode and not name:
        return jsonify({
            "error": "Provide either barcode or name"
        }), 400

    # Search OpenFoodFacts
    if barcode:
        product = search_by_barcode(barcode)

        if product is None:
            return jsonify({
                "error": "Product not found"
            }), 404

    else:
        products = search_by_name(name)

        if not products:
            return jsonify({
                "error": "Product not found"
            }), 404

        # Use the first matching product
        product = products[0]

    # Create a local inventory item
    new_id = max(
        (item["id"] for item in inventory),
        default=0
    ) + 1

    new_item = {
        "id": new_id,
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "barcode": product.get("barcode", ""),
        "price": data.get("price", 0),
        "stock": data.get("stock", 0),
        "ingredients_text": product.get(
            "ingredients_text",
            ""
        )
    }

    inventory.append(new_item)

    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(debug=True)