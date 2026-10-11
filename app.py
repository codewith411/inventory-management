from flask import Flask, jsonify, request

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


if __name__ == "__main__":
    app.run(debug=True)