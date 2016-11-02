import random

from google.appengine.ext import ndb


class Card(ndb.Model):
    """Card object"""
    game = ndb.KeyProperty(required=True, kind='Game')
    suit = ndb.StringProperty(required=True)
    value = ndb.IntegerProperty(required=True)
    index = ndb.IntegerProperty(required=True, default=0)
    matched = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def dispatch_cards_for_game(cls, game):
        """Create a list playing cards shuffled without joker"""
        cards = []
        for suit in ['clubs', 'diamonds', 'spades', 'hearts']:
            for value in range(1, 14):
                card = Card(game=game.key, suit=suit, value=value)
                cards.append(card)
        random.shuffle(cards)
        for index, card in enumerate(cards):
            card.index = index
        ndb.put_multi(cards)

    @classmethod
    def delete_cards_for_game(cls, game):
        """Delete cards of a finished game"""
        cards = Card.query(Card.game == game.key).fetch()
        for card in cards:
            card.key.delete()