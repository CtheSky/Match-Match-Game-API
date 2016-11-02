from protorpc import messages


# ----- Shared Protorpc Message Forms ------
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


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)