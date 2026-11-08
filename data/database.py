"""Set up the SQLite database using the schema defined in schema.sql."""    
import sqlite3
from pathlib import Path
import data.data_mcm as dm
import data.data_decks as dd
import data.data_cards as dc

DATABASE_FILE = Path(__file__).with_name("database.db") # Path to the SQLite database file
SCHEMA_FILE = Path(__file__).with_name("schema.sql") # Path to the schema.sql file
JSON_DIR = Path(__file__).parent / "json_files" # Directory containing JSON files
JSON_DECKS_DIR = JSON_DIR / "decks" # Directory containing deck JSON files



def main():
    """Main function to set up the database and create the table."""
    conn = sqlite3.connect(DATABASE_FILE)
    print(f"Connected to database: {DATABASE_FILE}")

    if conn is None:
        return
    try:
        create_tables(conn)

        with conn:
            price_data = dm.load_products_data("prices")
            nonsingle_data = dm.load_products_data("nonsingles")

            nonsingles_parsed = dm.parse_products_data(nonsingle_data, price_data)

            deck_paths = dd.load_paths(JSON_DECKS_DIR)
            decks_data = dd.load_decks(deck_paths)

            registered_mcm_ids = set()


            for deck_data in decks_data:
                deck = dd.create_deck_object(deck_data)
                if deck is None:
                    print(f"Failed to create deck object for {deck.get('name')!r}")
                    continue

                deck = dd.complete_deck_object(
                    nonsingles_parsed,
                    registered_mcm_ids,
                    deck,
                    dm.normalize_name(deck.name))

                if deck.mcm_id is not None:
                    registered_mcm_ids.add(deck.mcm_id)

                insert_deck(conn, deck)

                decklist = dd.create_decklist(deck_data, deck.deck_id)

                for card in decklist:
                    insert_card(conn, dc.create_card_object(price_data, card))
                    insert_deckcard(conn, card)
    finally:
        conn.close()

def create_tables(conn):
    """ create tables from the schema file """
    try:
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        print("Tables created successfully.")
    except sqlite3.Error as e:
        print(e)

    return

def insert_deck(conn, deck):
    """Inserts deck data into database"""
    conn.execute(
        """
        INSERT INTO decks (
            deck_id, deck_name, product_type, mcm_id,
            price_low, price_avg, price_trend
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(deck_id) DO UPDATE SET
            deck_name = excluded.deck_name,
            product_type = excluded.product_type,
            mcm_id = excluded.mcm_id,
            price_low = excluded.price_low,
            price_avg = excluded.price_avg,
            price_trend = excluded.price_trend
        """,
        (
            deck.deck_id,
            deck.name,
            deck.product_type,
            deck.mcm_id,
            deck.price_low,
            deck.price_avg,
            deck.price_trend,
        ),
    )
    return

def insert_card(conn, card):
    """Inserts card data into database"""
    conn.execute(
        """
        INSERT INTO cards (
            card_id, card_name, mcm_id, price_low,
            price_avg, price_trend, scryfall_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(card_id) DO UPDATE SET
            card_name = excluded.card_name,
            mcm_id = excluded.mcm_id,
            price_low = excluded.price_low,
            price_avg = excluded.price_avg,
            price_trend = excluded.price_trend,
            scryfall_id = excluded.scryfall_id
        """,
        (
            card.card_id,
            card.name,
            card.mcm_id,
            card.price_low,
            card.price_avg,
            card.price_trend,
            card.scryfall_id,
        ),
    )
    return

def insert_deckcard(conn, deck_card):
    """Inserts deckcard data into database"""
    conn.execute(
        """
        INSERT INTO deck_cards (
            deck_id, card_id, is_foil, quantity, board_section
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(deck_id, card_id, is_foil, board_section)
        DO UPDATE SET quantity = excluded.quantity
        """,
        (
            deck_card.deck_id,
            deck_card.card_id,
            deck_card.is_foil,
            deck_card.quantity,
            deck_card.board_section,
        ),
    )
    return

if __name__ == "__main__":
    main()
