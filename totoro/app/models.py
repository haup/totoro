from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.exceptions import ValidationError
from random import shuffle
import sys

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
        print(list(json_post.get('name')), file=sys.stderr)
        name = json_post.get('name')
        email = json_post.get('email')
        if name is None or email is None:
            raise ValidationError('post has an empty body')
        return Player(name=name, email=email)


class Tournament(db.Model):

    """Class Tournament"""

    __tablename__ = 'tournament'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(120), nullable=False)
    modus = db.Column(db.String(120), nullable=False)
    set_count = db.Column(db.Integer, primary_key=True)
    teams = db.relationship("Team", backref="tournament", lazy='dynamic')
    parent = db.Column(db.Integer)
    max_phase = db.Column(db.Integer)


    def __repr__(self):
            return '<Tournament: %d>' % (self.id)

    # Ranking is reversed!
    def generate_ranking(self): 
        ranking = []
        teams = Team.query.filter_by(tournament_id=self.id).all()
        phase = db.session.query(func.max(Match.phase).label('max_phase')).filter_by(tournament_id=self.id).one()[0]
        matches = Match.query.filter_by(tournament_id=self.id, phase=phase).all()
        if matches is None:
            random.shuffle(teams)
            for team in teams:
                ranking.append([team.id, 0, 0, 0])
        else:
            for team in teams:
                ranking.append([team, team.points, Tournament.calculate_buchholz1(team), Tournament.calculate_buchholz2(team)])
                sorted(ranking, key=lambda x: (x[1], -x[2], -x[3]))
        return ranking, phase


    def draw_round(self, ranking, phase):
        used = []
        teams = Tournament.get_teams_from_ranking(ranking)
        for i, current_team in enumerate(teams):
            if current_team in used:
                continue
            used.append(current_team)
            j = i + 1
            while teams[j] in used: # or teams[j] in looping_player[4]:
                j += 1
            used.append(teams[j])
            match = Match(team_a=current_team.id, team_b=teams[j].id, phase=phase + 1, tournament_id = self.id)
            db.session.add(match)
        db.session.commit()

    def finish_match(self, id):
        # If alreasy done then clause, set around
        match = Match.query.filter_by(id=id).first()
        set_count = Tournament.query.filter_by(id=match.tournament_id).first().set_count
        sets = Set.query.filter_by(match_id=match.id).all()
        team_a = Team.query.filter_by(id=match.team_a).first()
        team_b = Team.query.filter_by(id=match.team_b).first()
        team_a_sets = 0
        for set in sets:
            if set.score_a >= 5:
                team_a_sets += 1
        team_b_sets = len(sets) - team_a_sets
        if team_a_sets == set_count or team_b_sets == set_count:
            match.over = True
            team_a.history = ('' if not team_a.history else team_a.history) + str(team_b.id) + "," 
            team_b.history = ('' if not team_b.history else team_b.history) + str(team_a.id) + ","
            if team_a_sets == set_count:
                team_a.points = (0 if not team_a.points else team_a.points) + 1
            else:
                team_b.points = (0 if not team_b.points else team_b.points) + 1
        db.session.commit()

    @staticmethod
    def calculate_buchholz1(team):
        buchholz1 = 0
        for opponent in team.history.split(','):
            buchholz1 += Team.query.filter_by(id=opponent).first().points
        return buchholz1

    @staticmethod
    def calculate_buchholz2(team):
        buchholz2 = 0
        for opponent in team.history.split(','):
            o = Team.query.filter_by(id=opponent).first()
            buchholz2 += Tournament.calculate_buchholz1(o)
        return buchholz2

    @staticmethod
    def get_teams_from_ranking(ranking:list):
        return [x[0] for x in ranking]


class Team(db.Model):
    """Class Team"""

    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column('last_updated', db.DateTime, onupdate=datetime.now)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    players = db.relationship("Player", secondary=association_table, backref="team")
    points = db.Column(db.Integer, default=0)
    history = db.Column(db.String(120))

    def __repr__(self):
            return '<Team: %d>' % (self.id)


class Match(db.Model):

    """docstring for Games"""

    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    team_a = db.Column(db.Integer, db.ForeignKey('team.id'))
    team_b = db.Column(db.Integer, db.ForeignKey('team.id'))
    sets = db.relationship("Set", backref="match", lazy='dynamic')
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    phase = db.Column(db.Integer, default=0)
    over = db.Column(db.Boolean)

    def __repr__(self):
        return '<Game %d went >' % (self.id)

    def to_json(self):
        json_match = {
            'url': url_for('api.get_match', match_id=self.id, _external=True),
            'id': self.id,
            'team_a': self.team_a,
            'team_b': self.team_b,
            'sets': [set.to_json() for set in self.sets.all()],
            'tournament_id': self.tournament_id,
            'phase': self.phase,
            'over': self.over
        }
        return json_match


class Set(db.Model):

    __tablename__ = 'sets'
    id = db.Column(db.Integer, primary_key=True)
    score_a = db.Column(db.Integer, nullable=False)
    score_b = db.Column(db.Integer, nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    @staticmethod
    def check_if_match_exists(match_id):
        return True if Match.query.filter_by(id=match_id).count() == 1 else False

    def __repr__(self):
        return '<Set %d>' % (self.id)

    def to_json(self):
        json_match = {
            'url': url_for('api.get_set_of_match', match_id=self.match_id, set_id=self.id, _external=True),
            'id': self.id,
            'score_a': self.score_a,
            'score_b': self.score_b,
            'match_id': self.match_id
        }
        return json_match

    def from_json(json_post):
        match_id = json_post.get('match_id')
        score_a = json_post.get('score_a')
        score_b = json_post.get('score_b')
        if Set.check_if_match_exists(match_id) is False:
            raise ValidationError('')
        highest_id = db.session.query(func.max(Set.id).label('max_id')).one()[0]
        return Set(id=highest_id + 1, score_a=score_a, score_b=score_b, match_id=match_id)
