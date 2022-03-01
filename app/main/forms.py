from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField

from app.validators import validate_ru_number


class SearchUserForm(FlaskForm):
    username = StringField('Username')
    phone_number = StringField('PhoneNumber', validators=[validate_ru_number])
    submit = SubmitField('Search contact')


class RelationForm(FlaskForm):
    username = StringField('Username')
    note = StringField('Note')
    submit_rel = SubmitField('Add')


class ChatForm(FlaskForm):
    message = StringField('Message')
    submit_send = SubmitField('Send message')


class CreateChatForm(FlaskForm):
    users = SelectMultipleField('Contacts:')
    submit_adding_user = SubmitField('Add contacts in this chat')

    def __init__(self, choices=["You haven't contacts"]):
        super().__init__()
        self.users.choices = choices


class ChangeChatNameForm(FlaskForm):
    new_name = StringField('New chat name')
    submit_change = SubmitField('Change chat name')
