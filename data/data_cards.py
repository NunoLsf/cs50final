"""Data handling for card data"""
import data.data_mcm as dm

class Card:
    """Class representing a card."""

    def __init__(
        self,
        card_id,
        name,
        scryfall_id,
        mcm_id,
        price_low=None,
        price_avg=None,
        price_trend=None
    ):
        self.card_id = card_id
        self.name = name
        self.scryfall_id = scryfall_id
        self.mcm_id = mcm_id
        self.price_low = price_low
        self.price_avg = price_avg
        self.price_trend = price_trend

def create_card_object(price_data, deckcard):
    """Compile card data from deckcard object and price data"""
    card_id = deckcard.card_id
    name = deckcard.name
    scryfall_id = deckcard.scryfall_id
    mcm_id = deckcard.mcm_id
    price_low = None
    price_avg = None
    price_trend = None

    if mcm_id is not None:
        prices = dm.get_prices(price_data, mcm_id)
        if prices is not None and len(prices) == 3:
            price_low, price_avg, price_trend = prices

    return Card(card_id, name, scryfall_id, mcm_id, price_low, price_avg, price_trend)
