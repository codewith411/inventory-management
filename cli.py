import requests


BASE_URL = "http://127.0.0.1:5000"


def get_inventory():
    """Get all inventory items from the Flask API."""
    response = requests.get(f"{BASE_URL}/inventory")
    response.raise_for_status()
    return response.json()


def get_inventory_item(item_id):
    """Get one inventory item by ID."""
    response = requests.get(
        f"{BASE_URL}/inventory/{item_id}"
    )
    return response


def create_inventory_item(item):
    """Create a new inventory item."""
    response = requests.post(
        f"{BASE_URL}/inventory",
        json=item
    )
    return response


def update_inventory_item(item_id, updates):
    """Update an inventory item."""
    response = requests.patch(
        f"{BASE_URL}/inventory/{item_id}",
        json=updates
    )
    return response


def delete_inventory_item(item_id):
    """Delete an inventory item."""
    response = requests.delete(
        f"{BASE_URL}/inventory/{item_id}"
    )
    return response


def search_product(barcode=None, name=None):
    """Search OpenFoodFacts through the Flask API."""

    params = {}

    if barcode:
        params["barcode"] = barcode

    if name:
        params["name"] = name

    response = requests.get(
        f"{BASE_URL}/products/search",
        params=params
    )

    return response


def import_product(product_data):
    """Import an OpenFoodFacts product into inventory."""
    response = requests.post(
        f"{BASE_URL}/inventory/import",
        json=product_data
    )
    return response


def view_inventory():
    """Display all inventory items."""

    try:
        items = get_inventory()

        print("\n=== INVENTORY ===")

        if not items:
            print("Inventory is empty.")
            return

        for item in items:
            print(
                f"ID: {item['id']} | "
                f"Product: {item['product_name']} | "
                f"Brand: {item['brands']} | "
                f"Price: {item['price']} | "
                f"Stock: {item['stock']}"
            )

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def view_item():
    """Ask for an ID and display one inventory item."""

    item_id = input("Enter inventory ID: ")

    try:
        response = get_inventory_item(item_id)

        if response.status_code == 200:
            item = response.json()

            print("\n=== INVENTORY ITEM ===")
            print(f"ID: {item['id']}")
            print(f"Product: {item['product_name']}")
            print(f"Brand: {item['brands']}")
            print(f"Barcode: {item['barcode']}")
            print(f"Price: {item['price']}")
            print(f"Stock: {item['stock']}")
            print(f"Ingredients: {item['ingredients_text']}")

        else:
            print(response.json().get("error", "Item not found."))

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def add_item():
    """Create a new inventory item."""

    print("\n=== ADD INVENTORY ITEM ===")

    item = {
        "product_name": input("Product name: "),
        "brands": input("Brand: "),
        "barcode": input("Barcode: "),
        "price": float(input("Price: ")),
        "stock": int(input("Stock: ")),
        "ingredients_text": input("Ingredients: ")
    }

    try:
        response = create_inventory_item(item)

        if response.status_code == 201:
            print("\nItem added successfully!")
            print(response.json())

        else:
            print(response.json().get("error", "Unable to add item."))

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def update_item():
    """Update the price and/or stock of an inventory item."""

    print("\n=== UPDATE INVENTORY ITEM ===")

    item_id = input("Enter inventory ID: ")

    updates = {}

    price = input("New price (press Enter to skip): ")

    if price:
        updates["price"] = float(price)

    stock = input("New stock (press Enter to skip): ")

    if stock:
        updates["stock"] = int(stock)

    if not updates:
        print("No changes entered.")
        return

    try:
        response = update_inventory_item(
            item_id,
            updates
        )

        if response.status_code == 200:
            print("\nItem updated successfully!")
            print(response.json())

        else:
            print(response.json().get("error", "Unable to update item."))

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def delete_item():
    """Delete an inventory item."""

    print("\n=== DELETE INVENTORY ITEM ===")

    item_id = input("Enter inventory ID: ")

    try:
        response = delete_inventory_item(item_id)

        if response.status_code == 204:
            print("Item deleted successfully!")

        else:
            print(response.json().get("error", "Unable to delete item."))

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def find_product():
    """Search OpenFoodFacts by barcode or product name."""

    print("\n=== FIND PRODUCT ===")
    print("1. Search by barcode")
    print("2. Search by name")

    choice = input("Choose an option: ")

    try:
        if choice == "1":
            barcode = input("Enter barcode: ")

            response = search_product(
                barcode=barcode
            )

            if response.status_code == 200:
                product = response.json()

                print("\n=== PRODUCT FOUND ===")
                print(f"Product: {product['product_name']}")
                print(f"Brand: {product['brands']}")
                print(f"Barcode: {product['barcode']}")
                print(
                    f"Ingredients: "
                    f"{product['ingredients_text']}"
                )

            else:
                print(
                    response.json().get(
                        "error",
                        "Product not found."
                    )
                )

        elif choice == "2":
            name = input("Enter product name: ")

            response = search_product(name=name)

            if response.status_code == 200:
                products = response.json()

                if not products:
                    print("No products found.")
                    return

                print("\n=== PRODUCTS FOUND ===")

                for index, product in enumerate(
                    products,
                    start=1
                ):
                    print(
                        f"{index}. "
                        f"{product['product_name']} | "
                        f"{product['brands']} | "
                        f"{product['barcode']}"
                    )

            else:
                print(
                    response.json().get(
                        "error",
                        "Search failed."
                    )
                )

        else:
            print("Invalid option.")

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def import_external_product():
    """Import an OpenFoodFacts product into inventory."""

    print("\n=== IMPORT FROM OPENFOODFACTS ===")
    print("1. Import by barcode")
    print("2. Import by product name")

    choice = input("Choose an option: ")

    try:
        if choice == "1":
            barcode = input("Enter barcode: ")
            price = float(input("Local price: "))
            stock = int(input("Initial stock: "))

            data = {
                "barcode": barcode,
                "price": price,
                "stock": stock
            }

        elif choice == "2":
            name = input("Enter product name: ")
            price = float(input("Local price: "))
            stock = int(input("Initial stock: "))

            data = {
                "name": name,
                "price": price,
                "stock": stock
            }

        else:
            print("Invalid option.")
            return

        response = import_product(data)

        if response.status_code == 201:
            print("\nProduct imported successfully!")
            print(response.json())

        else:
            print(
                response.json().get(
                    "error",
                    "Unable to import product."
                )
            )

    except requests.RequestException as error:
        print(f"Error connecting to API: {error}")


def show_menu():
    """Display the main CLI menu."""

    print("\n")
    print("==============================")
    print("   INVENTORY MANAGEMENT CLI")
    print("==============================")
    print("1. View all inventory")
    print("2. View inventory item")
    print("3. Add inventory item")
    print("4. Update inventory item")
    print("5. Delete inventory item")
    print("6. Find OpenFoodFacts product")
    print("7. Import OpenFoodFacts product")
    print("8. Exit")
    print("==============================")


def main():
    """Run the inventory management CLI."""

    while True:
        show_menu()

        choice = input("Choose an option: ")

        if choice == "1":
            view_inventory()

        elif choice == "2":
            view_item()

        elif choice == "3":
            add_item()

        elif choice == "4":
            update_item()

        elif choice == "5":
            delete_item()

        elif choice == "6":
            find_product()

        elif choice == "7":
            import_external_product()

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1-8.")


if __name__ == "__main__":
    main()
