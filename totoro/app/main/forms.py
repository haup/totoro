from flask_wtf import Form
from flask import current_app
from .. import db
from ..models import User, Player, Team, Tournament

from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('Who are you?', validators=[Required()])
    submit = SubmitField('Submit')


class PlayerForm(Form):
    name = StringField("Name:", validators=[Required()])
    email = StringField("Mail", validators=[Required()])
    submit = SubmitField('Submit')


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
