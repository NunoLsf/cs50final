
"""Console interface for comparing sealed deck prices with their singles."""
import sqlite3

DATABASE_FILE = "data/database.db"

DECKS_SQL = """
    SELECT deck_id, deck_name, price_avg
    FROM decks
    ORDER BY deck_name
"""
# Copilot suggested a more complex query, but we can just use a simple join to get the card totals for each deck.
CARD_TOTALS_SQL = """
    SELECT
        dc.deck_id,
        SUM(COALESCE(c.price_avg, 0) * dc.quantity),
        SUM(CASE WHEN c.price_avg IS NULL THEN dc.quantity ELSE 0 END),
        SUM(dc.quantity)
    FROM deck_cards AS dc
    LEFT JOIN cards AS c ON c.card_id = dc.card_id
    GROUP BY dc.deck_id
"""

def main():
    """Run the console menu."""
    try:
        conn = sqlite3.connect(
            f"file:{DATABASE_FILE}?mode=ro",
            uri=True,
        )
    except sqlite3.OperationalError as error:
        print(f"Could not open {DATABASE_FILE}: {error}")
        print("Run the database setup before starting the app.")
        return

    try:
        while True:
            print(
                "\nDeck Price Explorer\n"
                "1. 10 most expensive sealed decks\n"
                "2. 10 best gross spreads\n"
                "3. Search decks by name\n"
                "4. Exit"
            )
            choice = input("Choose an option: ").strip()

            if choice == "1":
                show_most_expensive(conn)
            elif choice == "2":
                show_best_spread(conn)
            elif choice == "3":
                search_decks(conn)
            elif choice == "4":
                print("Goodbye.")
                break
            else:
                print("Please choose 1, 2, 3, or 4.")
    finally:
        conn.close()

def format_price(price):
    """Format a numeric price, or mark it unavailable."""
    if price is None:
        return "N/A"
    return f"{price:,.2f}€"


def get_deck_values(conn):
    """Combine deck prices with separately calculated card totals."""
    decks = conn.execute(DECKS_SQL).fetchall()
    card_totals = {
        deck_id: (singles, missing_copies, card_copies)
        for deck_id, singles, missing_copies, card_copies
        in conn.execute(CARD_TOTALS_SQL)
    }

    rows = []
    for deck_id, name, sealed in decks:
        singles, missing_copies, card_copies = card_totals.get(
            deck_id, (0, 0, 0)
        )
        spread = None
        if sealed is not None and card_copies > 0:
            spread = singles - sealed

        rows.append(
            (
                deck_id,
                name,
                sealed,
                singles,
                missing_copies,
                card_copies,
                spread,
            )
        )

    return rows


def show_decks(rows):
    """Print deck prices and singles totals."""
    if not rows:
        print("No matching decks found.")
        return

    print(
        f"\n{'Deck':50} {'Sealed':>12} {'Singles sum':>14} "
        f"{'Priced/total':>14} {'Spread':>12}"
    )
    print("-" * 112)

    for row in rows:
        _, name, sealed, singles, missing_copies, card_copies, spread = row
        priced_copies = card_copies - missing_copies
        copy_count = f"{priced_copies}/{card_copies}"

        print(
            f"{name[:50]:50} "
            f"{format_price(sealed):>12} "
            f"{format_price(singles):>14} "
            f"{copy_count:>14} "
            f"{format_price(spread):>12}"
        )


def show_most_expensive(conn):
    """Show the ten decks with the highest available sealed average price."""
    rows = [row for row in get_deck_values(conn) if row[2] is not None]
    rows.sort(key=lambda row: row[2], reverse=True)
    rows = rows[:10]
    show_decks(rows)


def show_best_spread(conn):
    """Show the ten highest spreads using available card prices."""
    rows = [row for row in get_deck_values(conn) if row[6] is not None]
    rows.sort(key=lambda row: row[6], reverse=True)
    rows = rows[:10]
    show_decks(rows)


def search_decks(conn):
    """Search deck names and show up to twenty matches."""
    search_term = input("Enter part of a deck name: ").strip()
    if not search_term:
        print("Please enter a search term.")
        return

    rows = [
        row for row in get_deck_values(conn)
        if search_term.casefold() in row[1].casefold()
    ][:20]
    show_decks(rows)

if __name__ == "__main__":
    main()
