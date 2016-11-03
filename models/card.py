import random

from protorpc import messages
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
        """Delete cards of given game"""
        cards = Card.query(Card.game == game.key).fetch()
        for card in cards:
            card.key.delete()

    @classmethod
    def get_cards_for_game(cls, game):
        """Get cards of given game"""
        return Card.query(Card.game == game.key).fetch()

    def to_form(self):
        form = CardForm()
        form.suit = self.suit
        form.value = self.value
        form.index = self.index
        form.matched = self.matched
        return form


# ----- Protorpc Message Forms ------
class CardForm(messages.Message):
    """CardForm for card information"""
    suit = messages.StringField(1, required=True)
    value = messages.IntegerField(2, required=True)
    index = messages.IntegerField(3, required=True)
    matched = messages.BooleanField(4, required=True)


class CardForms(messages.Message):
    """Return multiple CardForms"""
    items = messages.MessageField(CardForm, 1, repeated=True)
