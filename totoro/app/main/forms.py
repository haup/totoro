from flask_wtf import Form
from flask import current_app
from .. import db
from ..models import User, Player, Team, Tournament
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import StringField, SubmitField, IntegerField, SelectField, TextAreaField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required


class SearchForm(Form):
    search = StringField('search', validators=[DataRequired()])


class NameForm(Form):
    name = StringField('Who are you?', validators=[Required()])
    submit = SubmitField('Submit')

class PlayerForm(Form):
    name = StringField("Name:", validators=[Required()])
    email = StringField("Mail", validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')



class EditPlayerForm(Form):
    name = StringField("Edit New Player´s name:", validators=[Required()])
    email = StringField("Edit New Player´s Mail", validators=[Required()])
    submit = SubmitField('Submit')


class TeamForm(Form):

    def fill_field():
        return Player.query

    player_a = QuerySelectField(query_factory=fill_field)
    player_b = QuerySelectField(query_factory=fill_field)
    submit = SubmitField('Submit')


class TournamentForm(Form):
    name = StringField("Name:", validators=[Required()])
    modus = StringField("Modus:", validators=[Required()])
    set_count = StringField("Count of Sets:", validators=[Required()])
    max_phase = StringField("Max Phase:", validators=[Required()])
    submit = SubmitField('Submit')
