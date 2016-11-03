from datetime import date

from models.game import Game
from models.card import Card
from models.history import History
from models.score import Score
from models.message_form import MatchResultForm


class GameLogic:
    def __init__(self):
        pass

    @classmethod
    def match_pair(cls, game, pair_1, pair_2):
        """Match a pair and update game state"""
        game.attempts += 1
        game.put()
        card_1 = Card.query(Card.game == game.key).filter(Card.index == pair_1).get()
        card_2 = Card.query(Card.game == game.key).filter(Card.index == pair_2).get()

        if card_1.matched or card_2.matched:
            raise RuntimeError('Could not rematch a matched card')

        form = MatchResultForm()
        if card_1.value == card_2.value:
            card_1.matched = True
            card_1.put()
            card_2.matched = True
            card_2.put()
            game.matched += 2
            game.put()
            form.message = 'Success'
        else:
            form.message = 'Fail'

        # Construct return info form
        form.card_1 = card_1.to_form()
        form.card_2 = card_2.to_form()
        form.matched_count = game.matched

        if game.matched == 52:
            game.game_over = True
            game.put()
            Card.delete_cards_for_game(game)

            # Update average attempts of user
            user = game.user.get()
            games = Game.get_user_finished_games(user)
            count = len(games)
            if user.average_attempts == float('inf'):
                user.average_attempts = 0
            user.average_attempts = ((count - 1) * user.average_attempts + game.attempts) / count
            user.put()

            score = Score(user=game.user, date=date.today(), attempts=game.attempts)
            score.put()
            form.message = 'Win'

        # Create history log of this guess
        History.create_history(game=game,
                               card_1=card_1,
                               card_2=card_2,
                               message=form.message)
        return form