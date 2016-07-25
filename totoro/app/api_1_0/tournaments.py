from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from .. import auth
from ..models import Tournament, Team, Player


@api.route('/tournaments')
def get_tournaments():
    tournaments = Tournament.query.all()
    return jsonify({'Tournaments':
                    [tournament.to_json() for tournament in tournaments]})


@api.route('/tournaments/<int:id>')
def get_tournament(id):
    tournament = Tournament.query.get_or_404(id)
    return jsonify(tournament.to_json())


@api.route('/tournament/<int:id>/teams', methods=['GET'])
def get_teams_of_tournaments():
    tournament = Tournament.query.get_or_404(id)
    teams = Team.query.filter_by(tournament_id=id)
    return jsonify({'Tournament': tournament.to_json(),
                    'Teams': [team.to_json() for team in teams]})
