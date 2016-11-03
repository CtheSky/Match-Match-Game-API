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

        # Create history log
        History.create_history(game=game,
                               card_1=card_1,
                               card_2=card_2,
                               message=form.message)
        return form

    @classmethod
    def make_game_easier(cls, game, hint_num):
        cards = Card.get_cards_for_game(game)
        unmatched_cards = filter(lambda c: not c.matched, cards)
        hint_histories = []

        while game.matched != 52 and hint_num > 0:
            card_1 = unmatched_cards[0]
            card_2 = filter(lambda c: c != card_1 and c.value == card_1.value, unmatched_cards)[0]
            # Update game state
            card_1.matched = True
            card_2.matched = True
            game.matched += 2
            game.attempts += 1
            hint_num -= 1
            # Update card state unmatched card list
            unmatched_cards.remove(card_1)
            unmatched_cards.remove(card_2)
            card_1.put()
            card_2.put()
            # Create history log
            history = History.create_history(game=game, card_1=card_1, card_2=card_2, message='Hint Match')
            hint_histories.append(history)

        game.put()
        return hint_histories








