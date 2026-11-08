"""Data handling for Deck JSON files"""
import json

# CS: stands for Copilot Suggestion
CARD_ZONES = ("mainBoard", "sideBoard", "commander", "planes", "schemes")

class DeckCard:
    """Class representing a deck card"""
    def __init__(
            self,
            deck_id,
            card_id,
            is_foil,
            quantity,
            board_section,
            name,
            mcm_id,
            scryfall_id
    ):
        self.deck_id = deck_id
        self.card_id = card_id
        self.is_foil = is_foil
        self.quantity = quantity
        self.board_section = board_section
        self.name = name
        self.mcm_id = mcm_id
        self.scryfall_id = scryfall_id


class Deck:
    """Class representing a deck."""

    def __init__(
        self,
        deck_id,
        name,
        product_type,
        mcm_id=None,
        price_low=None,
        price_avg=None,
        price_trend=None,
    ):
        """CS: Added optional parameters for mcm_id and price to
        the deck class constructor."""
        self.deck_id = deck_id
        self.name = name
        self.product_type = product_type
        self.mcm_id = mcm_id
        self.price_low = price_low
        self.price_avg = price_avg
        self.price_trend = price_trend

def create_deck_object(deck_data):
    """Parse deck data from a dictionary and return a deck object."""
    try:
        deck_id = deck_data.get("sealedProductUuids")[0]
        name = deck_data.get("name")
        product_type = deck_data.get("type")

        if None in (deck_id, name, product_type):
            # CS: Check for missing required fields and raised a ValueError if any are missing.
            missing_fields = ", ".join(
                field
                for field, value in (
                    ("deck_id", deck_id),
                    ("name", name),
                    ("product_type", product_type),
                )
                if value is None
            )
            raise ValueError(f"Missing required deck fields: {missing_fields}")

        return Deck(deck_id, name, product_type)

    except (AttributeError, TypeError, ValueError) as e:
        # CS: Specific exception types to the exception handling to catch missing required fields.
        print(f"Error parsing deck data: {e}")
        return None

def complete_deck_object(parsed_nonsingles, registered_mcm_ids, deck_object, normalized_name):
    """Completes deck object properties with nonsingle product properties."""
    for nonsingle in parsed_nonsingles:
        if (
            normalized_name == nonsingle.name
            and nonsingle.mcm_id not in registered_mcm_ids
        ):
            deck_object.mcm_id = nonsingle.mcm_id
            deck_object.price_low = nonsingle.prices[0]
            deck_object.price_avg = nonsingle.prices[1]
            deck_object.price_trend = nonsingle.prices[2]
            break

    return deck_object

def create_decklist(deck_data, deck_id):
    """Create a list containing deck cards"""
    decklist = []
    if deck_data:
        for zone in CARD_ZONES:
            board_section = zone
            cards = deck_data.get(zone)

            for card in cards:
                card_id = card.get("uuid")
                is_foil = 1 if card.get("isFoil") else 0
                quantity = card.get("count")
                name = card.get("name")
                mcm_id = card.get("identifiers").get("mcmId")
                scryfall_id = card.get("identifiers").get("scryfallId")

                decklist.append(DeckCard(deck_id, card_id, is_foil, quantity, board_section, name, mcm_id, scryfall_id))

    return decklist

def load_deck_data(deck_path):
    """Load deck data from a JSON file."""
    try:
        with open(deck_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            deck_data = data.get("data", {})
            return deck_data

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading deck data from {deck_path}: {e}")
        return None


def load_decks(deck_file_paths):
    """Process a list of deck JSON file paths and return a list of deck objects."""
    decks = []

    for deck_file_path in deck_file_paths:
        deck_data = load_deck_data(deck_file_path)
        if not deck_data:
            print(f"Failed to load deck data from {deck_file_path}")
            continue

        if deck_data.get("type") == "Commander Deck":
            decks.append(deck_data)
    return decks


def load_paths(json_decks_dir):
    """Return paths to deck JSON files."""
    if not json_decks_dir.is_dir():
        print(f"decks directory {json_decks_dir} does not exist or is not a directory.")
        return []

    return list(json_decks_dir.glob("*.json"))
