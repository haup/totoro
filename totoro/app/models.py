from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime
from . import db

Base = declarative_base()


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


association_table = db.Table('player_team',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
)


class Player(db.Model):
    """Class Player"""

    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '%r' % (self.name)

    def to_json(self):
        json_player = {
            'url': url_for('api.get_player', id=self.id, _external=True),
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }
        return json_player

    def from_json(json_post):
        name = json_post.get('name')
        email = json_post.get('email')
        if (name or email is None) or (name or email is ''):
            raise ValidationError('post has an empty body')
        return Player(name=name, email=email)


class Tournament(db.Model):
    """Class Tournament"""

    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(120), nullable=False)
    modus = db.Column(db.String(120), nullable=False)
    set_count = db.Column(db.Integer)
    teams = db.relationship("Team", backref="tournament", lazy='dynamic')
    parent = db.Column(db.Integer)
    max_phase = db.Column(db.Integer)

    def __repr__(self):
            return '<Tournament: %d>' % (self.id)


class Team(db.Model):
    """Class Team"""

    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column('last_updated', db.DateTime, onupdate=datetime.now)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    players = db.relationship("Player", secondary=association_table, backref="team")

    def __repr__(self):
            return '<Team: %d>' % (self.id)


class Match(db.Model):
    """docstring for Games"""

    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.Integer, db.ForeignKey('team.id'))
    team_b = db.Column(db.Integer, db.ForeignKey('team.id'))
    sets = db.relationship("Set", backref="match", lazy='dynamic')
    phase = db.Column(db.Integer)
    over = db.Column(db.Boolean)

    def __repr__(self):
        return '<Game %d went >' % (self.player)


class Set(db.Model):

    __tablename__ = 'sets'
    id = db.Column(db.Integer, primary_key=True)
    score_a = db.Column(db.Integer, nullable=False)
    score_b = db.Column(db.Integer, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    def __repr__(self):
        return '<Set %d>' % (self.id)
