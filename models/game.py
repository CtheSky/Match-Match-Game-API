from datetime import date

from protorpc import messages
from google.appengine.ext import ndb

from card import Card
from history import History
from score import Score
from message_form import MatchResultForm


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

    def match_pair(self, pair_1, pair_2):
        """Match a pair and update game state"""
        self.attempts += 1
        self.put()
        card_1 = Card.query(Card.game == self.key).filter(Card.index == pair_1).get()
        card_2 = Card.query(Card.game == self.key).filter(Card.index == pair_2).get()

        if card_1.matched or card_2.matched:
            raise RuntimeError('Could not rematch a matched card')

        form = MatchResultForm()
        if card_1.value == card_2.value:
            card_1.matched = True
            card_1.put()
            card_2.matched = True
            card_2.put()
            self.matched += 2
            self.put()
            form.message = 'Success'
        else:
            form.message = 'Fail'

        # Construct return info form
        form.matched_card_suit_1 = card_1.suit
        form.matched_card_value_1 = card_1.value
        form.matched_card_suit_2 = card_2.suit
        form.matched_card_value_2 = card_2.value
        form.matched_count = self.matched

        if self.matched == 52:
            self.game_over = True
            self.put()
            Card.delete_cards_for_game(self)

            # Update average attempts of user
            user = self.user.get()
            games = Game.get_user_finished_games(user)
            count = len(games)
            if user.average_attempts == float('inf'):
                user.average_attempts = 0
            user.average_attempts = ((count - 1) * user.average_attempts + self.attempts) / count
            user.put()

            score = Score(user=self.user, date=date.today(), attempts=self.attempts)
            score.put()
            form.message = 'Win'

        # Create history log of this guess
        History.create_history(game=self,
                               card_1=card_1,
                               card_2=card_2,
                               message=form.message)
        return form

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

