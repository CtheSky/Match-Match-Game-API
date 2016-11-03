from protorpc import messages
from card import CardForm


# ----- Shared Protorpc Message Forms ------
class MakeMatchForm(messages.Message):
    """Used to make a match in an existing game"""
    guess_pair_1 = messages.IntegerField(1, required=True)
    guess_pair_2 = messages.IntegerField(2, required=True)


class MatchResultForm(messages.Message):
    """Used to give result of a match"""
    card_1 = messages.MessageField(CardForm, 1, required=True)
    card_2 = messages.MessageField(CardForm, 2, required=True)
    matched_count = messages.IntegerField(3, required=True)
    message = messages.StringField(4, required=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)