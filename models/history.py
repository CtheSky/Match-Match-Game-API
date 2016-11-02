from protorpc import messages
from google.appengine.ext import ndb

from message_form import MatchResultForm


class History(ndb.Model):
    """History object"""
    game = ndb.KeyProperty(required=True, kind='Game')
    nth = ndb.IntegerProperty(required=True)
    matched = ndb.IntegerProperty(required=True)
    message = ndb.StringProperty(required=True)
    suit_1 = ndb.StringProperty(required=True)
    value_1 = ndb.IntegerProperty(required=True)
    suit_2 = ndb.StringProperty(required=True)
    value_2 = ndb.IntegerProperty(required=True)

    @classmethod
    def create_history(cls, game, card_1, card_2, message):
        """Create history of guess"""
        history = History(game=game.key,
                          nth=game.attempts,
                          matched=game.matched,
                          message=message,
                          suit_1=card_1.suit,
                          value_1=card_1.value,
                          suit_2=card_2.suit,
                          value_2=card_2.value,
                          )
        history.put()

    @classmethod
    def get_game_history(cls, game):
        """Return guess histories of game"""
        histories = History.query(History.game == game.key).fetch()
        return sorted(histories, key=lambda h: h.nth, reverse=True)

    def to_form(self):
        """Returns a MatchResultForm representation of the MatchResult"""
        form = MatchResultForm()
        form.matched_card_suit_1 = self.suit_1
        form.matched_card_value_1 = self.value_1
        form.matched_card_suit_2 = self.suit_2
        form.matched_card_value_2 = self.value_2
        form.matched_count = self.matched
        form.message = self.message
        return form


# ----- Protorpc Message Forms ------
class HistoryForms(messages.Message):
    """Return multiple histories"""
    items = messages.MessageField(MatchResultForm, 1, repeated=True)
