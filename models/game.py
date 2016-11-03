from datetime import date

from protorpc import messages
from google.appengine.ext import ndb

from card import Card


class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    attempts = ndb.IntegerProperty(required=True, default=0)
    matched = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        game = Game(user=user.key)
        game.put()
        Card.dispatch_cards_for_game(game)
        return game

    @classmethod
    def cancel_game(cls, game):
        """Cancel a game by deleting itself and its cards"""
        Card.delete_cards_for_game(game)
        game.key.delete()

    @classmethod
    def get_user_active_games(cls, user):
        """Return all active games of user"""
        return Game.query(Game.user == user.key).filter(Game.game_over == False).fetch()

    @classmethod
    def get_user_finished_games(cls, user):
        """Return all finished games of user"""
        return Game.query(Game.user == user.key).filter(Game.game_over == True).fetch()

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts = self.attempts
        form.matched = self.matched
        form.game_over = self.game_over
        form.message = message
        return form


# ----- Protorpc Message Forms ------
class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)
    matched = messages.IntegerField(3, required=True)
    game_over = messages.BooleanField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)


class GameForms(messages.Message):
    """Return multiple games"""
    items = messages.MessageField(GameForm, 1, repeated=True)

