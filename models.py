"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    average_attempts = ndb.FloatProperty(default=float('inf'))

    @classmethod
    def get_top_users(cls, limit):
        """Return top n users, n = limit"""
        return User.query().order(User.average_attempts).fetch(limit)

    def to_form(self):
        """Returns a UserAverageForm representation of the User"""
        form = UserAverageForm()
        form.user_name = self.name
        form.email = self.email
        if self.average_attempts == float('inf'):
            form.average_attempts = 'No game is finished.'
        else:
            form.average_attempts = str(self.average_attempts)
        return form

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


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    attempts = ndb.IntegerProperty(required=True)

    @classmethod
    def get_user_scores(cls, user):
        """Return all user scores"""
        return Score.query(Score.user == user.key).fetch()

    @classmethod
    def get_high_scores(cls, limit):
        """Return top n scores, n = limit"""
        return Score.query().order(Score.attempts).fetch(limit)

    def to_form(self):
        """Returns a ScoreForm representation of the Score"""
        form = ScoreForm()
        form.attempts = self.attempts
        form.date = str(self.date)
        form.user_name = self.user.get().name
        return form


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

class UserNameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)

class MakeMatchForm(messages.Message):
    """Used to make a match in an existing game"""
    guess_pair_1 = messages.IntegerField(1, required=True)
    guess_pair_2 = messages.IntegerField(2, required=True)

class MatchResultForm(messages.Message):
    """Used to give result of a match"""
    matched_card_value_1 = messages.IntegerField(1, required=True)
    matched_card_value_2 = messages.IntegerField(2, required=True)
    matched_card_suit_1 = messages.StringField(3, required=True)
    matched_card_suit_2 = messages.StringField(4, required=True)
    matched_count = messages.IntegerField(5, required=True)
    message = messages.StringField(6, required=True)

class HistoryForms(messages.Message):
    """Return multiple histories"""
    items = messages.MessageField(MatchResultForm, 1, repeated=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    attempts = messages.IntegerField(4, required=True)

class UserAverageForm(messages.Message):
    """Return user name and average attempts"""
    user_name = messages.StringField(1, required=True)
    average_attempts = messages.StringField(2, required=True)
    email = messages.StringField(3, required=False)

class UserAverageForms(messages.Message):
    """Return muliple UserAverageForm"""
    items = messages.MessageField(UserAverageForm, 1, repeated=True)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
