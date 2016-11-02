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


# ----- Protorpc Message Forms ------
class UserNameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class UserAverageForm(messages.Message):
    """Return user name and average attempts"""
    user_name = messages.StringField(1, required=True)
    average_attempts = messages.StringField(2, required=True)
    email = messages.StringField(3, required=False)


class UserAverageForms(messages.Message):
    """Return muliple UserAverageForm"""
    items = messages.MessageField(UserAverageForm, 1, repeated=True)

