from protorpc import messages
from google.appengine.ext import ndb


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
        return history

    @classmethod
    def get_game_history(cls, game):
        """Return guess histories of game"""
        histories = History.query(History.game == game.key).fetch()
        return sorted(histories, key=lambda h: h.nth, reverse=True)

    def to_form(self):
        """Returns a MatchResultForm representation of the MatchResult"""
        form = HistoryForm()
        form.card_suit_1 = self.suit_1
        form.card_value_1 = self.value_1
        form.card_suit_2 = self.suit_2
        form.card_value_2 = self.value_2
        form.matched_count = self.matched
        form.message = self.message
        return form


# ----- Protorpc Message Forms ------
class HistoryForm(messages.Message):
    """HistoryForm for history information"""
    card_value_1 = messages.IntegerField(1, required=True)
    card_value_2 = messages.IntegerField(2, required=True)
    card_suit_1 = messages.StringField(3, required=True)
    card_suit_2 = messages.StringField(4, required=True)
    matched_count = messages.IntegerField(5, required=True)
    message = messages.StringField(6, required=True)


class HistoryForms(messages.Message):
    """Return multiple histories"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)
