"""Data handling for MagicCardMarket JSON files."""
import json
import re
from pathlib import Path

#CS: stands for Copilot Suggestion

JSON_SINGLES_FILE = Path(__file__).parent / "json_files" / "products_singles_1.json"
JSON_NONSINGLES_FILE = Path(__file__).parent / "json_files" / "products_nonsingles_1.json"
JSON_PRICES_FILE = Path(__file__).parent / "json_files" / "price_guide_1.json"

JSON_FILES = {
    "singles": JSON_SINGLES_FILE,
    "nonsingles": JSON_NONSINGLES_FILE,
    "prices": JSON_PRICES_FILE
}

class Product:
    """Class representing a product's MCM relevant information."""
    def __init__(self, name, mcm_id, prices):
        self.name = name
        self.mcm_id = mcm_id
        self.prices = prices

# Name normalization functions for product names to ensure consistent comparisons

def normalize_name(name):
    """Normalize a product name for comparison."""
    if not isinstance(name, str):
        return None

    # Remove non-alphanumeric characters and convert to lowercase
    normalized_name = re.sub(r'[^a-zA-Z0-9]', '', name).lower()
    return normalized_name

def extract_product_name(name):
    """Extract a quoted product title, then normalize it for comparison."""
    # CS: Function made by Copilot
    if not isinstance(name, str):
        return None

    match = re.search(r'"([^"]+)"', name)
    if match:
        name = match.group(1)

    return normalize_name(name)

# Data extraction functions for MagicCardMarket JSON files

def get_mcm_id(parsed_products, deck_name, decks_with_mcm_ids):
    """Parse nonsingles data and return the ID of a specific product."""
    # Only decks require search by name, as singles are identified by their mtgjson_uuid.
    name = normalize_name(deck_name)
    for product in parsed_products:
        if product.get("name") == name and product.get("idProduct") not in decks_with_mcm_ids:
            return product.get("idProduct")
    return None

def get_prices(price_data, product_mcm_id):
    """Parse price data and return the average price of a specific product."""
    prices = price_data.get("priceGuides", [])
    for price_guide in prices:
        if price_guide.get("idProduct") == int(product_mcm_id):
            return (
                price_guide.get("low"),
                price_guide.get("avg"),
                price_guide.get("trend"),
            )
    return None

# Data loading and parsing functions for MagicCardMarket JSON files

def parse_products_data(products_data, price_data):
    """Parse product data and return a list of Product objects."""
    if products_data:
        nonsingles_products = products_data.get("products", [])
        parsed_products = []

        for product in nonsingles_products:
            name = extract_product_name(product.get("name"))
            mcm_id = product.get("idProduct")
            prices = get_prices(price_data, mcm_id)

            if name and mcm_id and prices:
                parsed_products.append(Product(name, mcm_id, prices))

        return parsed_products
    return

def load_products_data(catalog):
    """Load product data from a JSON file based on the catalog type."""
    if catalog not in JSON_FILES:
        print(f"Invalid catalog: {catalog}. Valid options are: {list(JSON_FILES.keys())}")
        return None

    file_path = JSON_FILES[catalog]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Loaded product data from {file_path}")
            return data

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading product data from {file_path}: {e}")
        return None
