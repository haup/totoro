from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Player


class CRUD():
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()


@api.route('/players')
def get_players():
    players = Player.query.all()
    return jsonify({'players': [player.to_json() for player in players]})

@api.route('/players/<int:id>')
def get_player(id):
    player = Player.query.get_or_404(id)
    return jsonify(player.to_json())

@api.route('/players', methods=['POST'])
def create_player():
    print(request)
    player = Player.from_json(request.json)
    db.session.add(player)
    db.session.commit()
    return jsonify(player.to_json()), 201, \
        {'Location': url_for('api.get_player', id=player.id)}
