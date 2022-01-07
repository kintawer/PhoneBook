from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


def validate_number(form, number):
    # ex 8 911 940 50 20
    # ex +7 911 940 50 20
    if not number.data:
        return

    if number.data[0] == '+':
        if not number.data[1:].isdigit():
            raise ValidationError('Please enter an integer phone number')
        if len(number.data) != 12:
            raise ValidationError('Please check phone number')
    else:
        if not number.data.isdigit():
            raise ValidationError('Please enter an integer phone number')
        if len(number.data) != 11:
            raise ValidationError('Please check phone number')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('PhoneNumber', validators=[validate_number])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SearchUserForm(FlaskForm):
    username = StringField('Username')
    phone_number = StringField('PhoneNumber', validators=[validate_number])
    submit = SubmitField('Search contact')


class RelationForm(FlaskForm):
    username = StringField('Username')
    note = StringField('Note')
    submit_rel = SubmitField('Add')


class ChatForm(FlaskForm):
    message = StringField('Message')
    submit_send = SubmitField('Send message')






