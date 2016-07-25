from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from .. import auth
from ..models import Player


@api.route('/players/<int:id>')
def get_player(id):
    player = Player.query.filter_by(id=id).one()
    return jsonify(player.to_json())
