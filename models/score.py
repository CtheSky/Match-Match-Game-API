from protorpc import messages
from google.appengine.ext import ndb


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


# ----- Protorpc Message Forms ------
class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    attempts = messages.IntegerField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)
