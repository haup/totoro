from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Tournament, Match, Set, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden




# GET für Tournament, Players und Teams
# all sets from match geht nicht...



@api.route('/matches', methods=["GET"])
@permission_required(Permission.SET)
def get_matches():
    matches = Match.query.all()
    return jsonify({'matches': [match.to_json() for match in matches]})


@api.route('/matches/<int:match_id>', methods=["GET"])
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    return jsonify(match.to_json())


@api.route('/matches/<int:match_id>/sets', methods=['GET'])
def get_sets_of_match(match_id):
    sets = [set for set in Set.query.filter_by(match_id=match_id).all()]
    return jsonify(sets.to_json())


@api.route('/matches/<int:match_id>/sets/<int:set_id>', methods=['GET'])
def get_set_of_match(match_id, set_id):
    set = Set.query.filter_by(id=set_id, match_id=match_id).one()
    return jsonify(set.to_json())


@api.route('/matches/<int:match_id>/sets', methods=['POST'])
def create_set_of_match(match_id):
    set = Set.from_json(request.json, match_id)
    db.session.add(set)
    db.session.commit()
    t_id = Match.query.filter_by(id=match_id).one().tournament_id
    tournament = Tournament.query.filter_by(id=t_id).one()
    tournament.finish_match(match_id)
    return jsonify(set.to_json()), 201, \
        {'url': url_for('api.get_set_of_match', set_id=set.id, match_id=match_id)}


@api.route('/matches/<int:match_id>/sets/<int:set_id>', methods=['PUT'])
def update_set_of_match(match_id, set_id):
    Set = Set.query.filter_by(id=set_id, match_id=match_id).one()
    posted_set = Set.from_json(request.json)
    if Set is not posted_set:
        Set = posted_set
        db.session.add(set)
        db.session.commit()
        return jsonify(set.to_json()), 200, \
            {'url': url_for('api.get_set_of_match', set_id=set.id, match_id=match_id)}
