from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from .. import auth
from ..models import Team


@api.route('/teams/<int:id>')
def get_team(id):
    team = Team.query.filter_by(id=id).one()
    return jsonify(team.to_json())
