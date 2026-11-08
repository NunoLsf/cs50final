# Deck Check
#### Video Demo: <URL HERE>
#### Description:

Deck Check is a Python command-line program for exploring the prices of Magic: The Gathering Commander decks.
It compares the average price of a complete sealed deck with the combined average prices of the individual cards listed inside that deck.
The goal is to make it easy to browse deck prices, compare the sealed value against the singles' value (cracked/open deck)
Prices are displayed in euros.
The comparison is a gross difference only, it does not account for marketplace fees, shipping, taxes, or the effort involved in selling individual cards.

The program works in the following order, from its source data to the results shown to the user:

- **1. Read the supplied data.** Local JSON inputs in `data/json_files/` include product and price-guide data, plus a `decks/` directory with deck lists. These files provide the names, identifiers, prices, and card contents used to build the local dataset. They are excluded from this repository because of their size. The included database lets the menu app run without them; rebuilding the database requires obtaining these JSON inputs separately. The app does not fetch current prices from the internet when the menu program runs.

- **2. Convert and match product information.** `data/data_mcm.py` loads product and price-guide JSON, looks up prices by product identifier, and normalizes names so deck products can be matched even when punctuation or capitalization differs. `data/data_decks.py` reads deck JSON, keeps Commander Deck products, and extracts cards from supported sections such as the main board, sideboard, and commander. `data/data_cards.py` creates card records and attaches available price information to cards.

- **3. Build the local database.** When the source JSON files are available, run `python -m data.database` from the project root to initialize and populate `data/database.db`. `data/database.py` coordinates the import: it applies `data/schema.sql`, processes the local price and deck data, then inserts or updates decks, cards, and deck-card quantities. SQLite stores these as three related kinds of records: decks, cards, and the cards belonging to each deck. The included database is what the menu app reads.

- **4. Calculate each deck’s comparison.** Run `python app.py` to start the console menu. `app.py` reads the database in read-only mode. For each deck, it adds the average prices of its listed card copies, multiplying each card’s price by its quantity. A card copy without a price contributes zero to the total, and the displayed priced/total count shows how many copies had prices available. The spread is the singles total minus the sealed deck’s average price; it is shown only when the sealed price is available and the deck contains card copies.

- **5. Choose a view from the menu.** The first option lists up to ten decks with the highest available sealed average prices. The second lists up to ten decks with the highest calculated gross spreads. The third searches deck names without regard to capitalization and displays up to twenty matches. The final option exits the program. If the database has not been created, run the setup command before starting the app.

The main project files are `app.py`, which implements the menu, calculations, and output; `data/database.py`, which builds the database; `data/schema.sql`, which defines its tables and relationships; and the three `data/data_*.py` modules, which handle importing and shaping the source data. The program uses only the Python standard library. To use the program, launch the app from the project root:

```bash
python app.py
```

- **Note:** Decklists were sourced from mtgjson.org, while price data was sourced from magiccardmarket.org.
