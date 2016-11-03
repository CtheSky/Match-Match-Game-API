# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import endpoints
from protorpc import remote, messages

from models.user import User, UserNameForm, UserAverageForms
from models.game import Game, GameForm, GameForms
from models.history import History, HistoryForms
from models.score import Score, ScoreForms
from models.message_form import MatchResultForm, MakeMatchForm, StringMessage

from game_logic import GameLogic
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(UserNameForm)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
GET_GAME_HISTORY_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MATCH_REQUEST = endpoints.ResourceContainer(
    MakeMatchForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))
NUM_LIMIT_REQUEST = endpoints.ResourceContainer(
    number_of_results=messages.IntegerField(1, default=10),)


@endpoints.api(name='guess_a_number', version='v1')
class GuessANumberApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        game = Game.new_game(user)
        game.put()
        return game.to_form('Good luck playing match-match!')


    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='cancel_game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel an unfinished game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        elif game.game_over:
            raise endpoints.ForbiddenException('Illegal action: Can\'t cancel a completed game!')
        else:
            Game.cancel_game(game)
            return game.to_form('Game has been canceled!')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a match!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MATCH_REQUEST,
                      response_message=MatchResultForm,
                      path='game/{urlsafe_game_key}',
                      name='make_match',
                      http_method='PUT')
    def make_match(self, request):
        """Makes a match. Returns matched cards' state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            raise endpoints.ForbiddenException('Illegal action: Game is already over.')

        pair_1 = request.guess_pair_1
        pair_2 = request.guess_pair_2
        if pair_1 == pair_2:
            raise endpoints.ForbiddenException('Illegal action: Two guess index must be different!')
        if pair_1 < 0 or pair_2 < 0 or pair_1 > 51 or pair_2 > 51:
            raise endpoints.ForbiddenException('Illegal action: Guess num must between 0 and 52!')

        try:
            return GameLogic.match_pair(game=game, pair_1=pair_1, pair_2=pair_2)
        except RuntimeError:
            raise endpoints.ForbiddenException('Illegal action: Could not rematch a matched card')


    @endpoints.method(request_message=GET_GAME_HISTORY_REQUEST,
                      response_message=HistoryForms,
                      path='game_history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return the guess history of given game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        histories = History.get_game_history(game)
        return HistoryForms(items=[h.to_form() for h in histories])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='get_user_active_games',
                      name='get_user_active_games',
                      http_method='GET')
    def get_user_active_games(self, request):
        """Return all of a User's active games."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games = Game.get_user_active_games(user)
        return GameForms(items=[g.to_form(message='User\'s active game') for g in games])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='get_user_finished_games',
                      name='get_user_finished_games',
                      http_method='GET')
    def get_user_finished_games(self, request):
        """Return all of a User's active games."""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games = Game.get_user_finished_games(user)
        return GameForms(items=[g.to_form(message='User\'s finished game') for g in games])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.get_user_scores(user)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=NUM_LIMIT_REQUEST,
                      response_message=ScoreForms,
                      path='high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Returns top n highest scores, n is given in request param"""
        limit = request.number_of_results
        if limit <= 0:
            raise endpoints.BadRequestException('Number_of_results must be greater than 0!')
        scores = Score.get_high_scores(limit=limit)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=NUM_LIMIT_REQUEST,
                      response_message=UserAverageForms,
                      path='user_rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Returns top n users, n is given in request param"""
        limit = request.number_of_results
        if limit <= 0:
            raise endpoints.BadRequestException('Number_of_results must be greater than 0!')
        users = User.get_top_users(limit=limit)
        return UserAverageForms(items=[u.to_form() for u in users])

api = endpoints.api_server([GuessANumberApi])
