PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS decks (
    deck_id TEXT PRIMARY KEY,
    deck_name TEXT NOT NULL,
    product_type TEXT NOT NULL,
    mcm_id INTEGER,
    price_low REAL,
    price_avg REAL,
    price_trend REAL
);

CREATE TABLE IF NOT EXISTS cards (
    card_id TEXT PRIMARY KEY,
    card_name TEXT NOT NULL,
    mcm_id INTEGER,
    price_low REAL,
    price_avg REAL,
    price_trend REAL,
    scryfall_id TEXT
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    is_foil INTEGER NOT NULL DEFAULT 0 CHECK (is_foil IN (0, 1)),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    board_section TEXT NOT NULL,
    PRIMARY KEY (deck_id, card_id, is_foil, board_section),
    FOREIGN KEY (deck_id) REFERENCES decks (deck_id),
    FOREIGN KEY (card_id) REFERENCES cards (card_id)
);
