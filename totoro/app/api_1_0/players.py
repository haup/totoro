from flask import jsonify
from . import api
from ..models import Player, Permission
from .decorators import permission_required


@api.route('/players/<int:id>')
@permission_required(Permission.SET)
def get_player(id):

    """ This methods queries a specific player
        from the database and returns it as json
        It is annotated with the route Annotation
        for representing an endpoint of the API
        Return: json of player
    """
    player = Player.query.filter_by(id=id).one()
    return jsonify(player.to_json())
