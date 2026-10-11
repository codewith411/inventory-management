import requests


OPENFOODFACTS_URL = "https://world.openfoodfacts.org"

HEADERS = {
    "User-Agent": "InventoryManagementApp/1.0 (Python)"
}


def search_by_barcode(barcode):
    """
    Search OpenFoodFacts using a product barcode.

    Returns a dictionary containing product information,
    or None if the product cannot be found or the request fails.
    """
    url = f"{OPENFOODFACTS_URL}/api/v2/product/{barcode}.json"

    params = {
        "fields": "product_name,brands,code,ingredients_text"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError):
        return None

    if data.get("status") != 1:
        return None

    product = data.get("product", {})

    return {
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "barcode": product.get("code", barcode),
        "ingredients_text": product.get("ingredients_text", "")
    }


def search_by_name(name):
    """
    Search OpenFoodFacts using a product name.

    Uses the legacy search endpoint because API v2 does
    not support general full-text product searches.

    Returns a list of matching products.
    """
    if not isinstance(name, str) or not name.strip():
        return []

    url = f"{OPENFOODFACTS_URL}/cgi/search.pl"

    params = {
        "search_terms": name.strip(),
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
        "fields": "product_name,brands,code,ingredients_text"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError):
        return []

    results = []

    for product in data.get("products", []):
        results.append({
            "product_name": product.get("product_name", ""),
            "brands": product.get("brands", ""),
            "barcode": product.get("code", ""),
            "ingredients_text": product.get(
                "ingredients_text", ""
            )
        })

    return results