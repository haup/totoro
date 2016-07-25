from flask import current_app, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.exceptions import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin
from random import shuffle
import sys, bleach, hashlib
import app
import flask_whooshalchemyplus as whooshalchemy

from datetime import datetime
from . import db, login_manager

Base = declarative_base()
enable_search = True


class Permission:
    SET = 0x04


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.SET, True),
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    avatar_hash = db.Column(db.String(32))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['TOTORO_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')


    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


association_table = db.Table('player_team',
    db.Column('player_id', db.Integer, db.ForeignKey('player.id')),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'))
)


class Player(db.Model):

    """Class Player"""

    __tablename__ = 'player'
    __searchable__ = ['name']
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
        if name is None or email is None:
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
            print("##########################")
            for team in teams:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>", team)
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

    def finish_match(self, match_id):
        # If alreasy done then clause, set around over-flag
        # TODO in match auslagern
        match = Match.query.filter_by(id=match_id).first()

        if match.over:
            return

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
            team_a.history = ('' if not team_a.history else team_a.history + ",") + str(team_b.id) 
            team_b.history = ('' if not team_b.history else team_b.history + ",") + str(team_a.id)
            if team_a_sets == set_count:
                team_a.points = (0 if not team_a.points else team_a.points) + 1
            else:
                team_b.points = (0 if not team_b.points else team_b.points) + 1
        db.session.commit()

    def check_if_phase_is_over(self):
        phase = db.session.query(func.max(Match.phase).label('max_phase')).filter_by(tournament_id=self.id).one()[0]
        matches_of_phase = Match.query.filter_by(tournament_id=id, phase=phase).all()
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        for match in matches:
            if match.over == False:
                return
        print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
        ranking, latest_phase  = generate_ranking()
        draw_round(ranking, phase)
        return True


    def to_json(self):
        json_tournament = {
            'url': url_for('api.get_tournament', id=self.id, _external=True),
            'id': self.id,
            'name': self.name,
            'modus': self.modus,
            'parent_id': self.parent if self.parent is not None else None,
            'max_phase': self.max_phase,
            'teams': [team.to_json() for team in self.teams]
        }
        return json_tournament


    @staticmethod
    def calculate_buchholz1(team):
        # team is none?
        #if not team:
        print("################################## Team", team)
        print("################################## Hist", team.history)

        buchholz1 = 0
        for opponent in team.history.split(','):
            if not opponent:
                print("##################", repr(opponent))
            buchholz1 += Team.query.filter_by(id=opponent).first().points
        return buchholz1

    @staticmethod
    def calculate_buchholz2(team):
        buchholz2 = 0
        if not team:
            print("################################## Team2")
        for opponent in team.history.split(','):
            if not team:
                print("##################################2", opponent)
            o = Team.query.filter_by(id=opponent).first()
            buchholz2 += Tournament.calculate_buchholz1(o)
        return buchholz2

    @staticmethod
    def get_teams_from_ranking(ranking: list):
        return [x[0] for x in ranking]


class Team(db.Model):
    """Class Team"""

    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    create_time = db.Column('last_updated', db.DateTime, onupdate=datetime.now)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))
    points = db.Column(db.Integer, default=0)
    history = db.Column(db.String(120))
    players = db.relationship("Player",
                              secondary=association_table, backref="team")

    def __repr__(self):
            return '<Team: %d>' % (self.id)

    def to_json(self):
        json_team = {
            'url': url_for('api.get_team', id=self.id, _external=True),
            'id': self.id,
            'players': [player.to_json() for player in self.players],
            'tournament_id': self.tournament_id,
            'history': self.history,
            'points': self.points,
        }
        return json_team


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

    def from_json(json_post, match_id):
        score_a = json_post.get('score_a')
        score_b = json_post.get('score_b')
        if Set.check_if_match_exists(match_id) is False:
            raise ValidationError('')
        highest_id = db.session.query(func.max(Set.id).label('max_id')).one()[0]
        return Set(id=highest_id + 1, score_a=score_a, score_b=score_b, match_id=match_id)


if enable_search:
    whooshalchemy.whoosh_index(app, Player)
