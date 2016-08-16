from flask_wtf import Form
from ..models import User, Player
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import StringField, SubmitField, SelectField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField


class PlayerForm(Form):

    """ This class represents a form to create a new player"""
    name = StringField('Name:', validators=[Required()])
    email = StringField('Mail', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):

    """ This class represents a form to edit a users profile name"""
    name = StringField('Real name', validators=[Length(0, 64)])
    submit = SubmitField('Submit')


class EditPlayerForm(Form):
    """ This class represents a form to edit a player"""
    name = StringField('Edit New Player´s name:', validators=[Required()])
    email = StringField('Edit New Player´s Mail', validators=[Required()])
    submit = SubmitField('Submit')


class TeamForm(Form):

    """ This class represents a form to create a new team"""
    def fill_field():

        """ This function simply returns
            a query object for a querySelectField
        """
        return Player.query

    player_a = QuerySelectField(query_factory=fill_field)
    player_b = QuerySelectField(query_factory=fill_field)
    submit = SubmitField('Add')


class TournamentForm(Form):

    """ This class represents a form to create or alter a tournament"""
    name = StringField('Name:', validators=[Required()])
    modus = StringField('Modus:', validators=[Required()])
    set_count = StringField('Count of Sets:', validators=[Required()])
    max_phase = StringField('Max Phase:', validators=[Required()])
    submit = SubmitField('Submit')


class KoTournamentForm(Form):

    """ This class represents a form to create or alter a tournament
        with a knock out elimination
    """
    name = StringField('Name:', validators=[Required()])
    modus = StringField('Modus:', validators=[Required()])
    set_count = StringField('Count of Sets:', validators=[Required()])
    submit = SubmitField('Submit')
