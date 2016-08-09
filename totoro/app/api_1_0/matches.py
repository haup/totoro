# from flask import jsonify, request, url_for
# from .. import db
# from ..models import Tournament, Match, Set, Permission
# from . import api
# from .decorators import permission_required
# from flask_login import login_required


# @api.route('/matches', methods=["GET"])
# @permission_required(Permission.SET)
# def get_matches():

#     """ This function queries all matches from the database and returns it as json
#         It is annotated with the route decorator for
#         representing an endpoint of the API
#         Return: json of matches
#     """
#     matches = Match.query.all()
#     return jsonify([match.to_json() for match in matches])


# @api.route('/matches/<int:match_id>', methods=["GET"])
# @permission_required(Permission.SET)
# def get_match(match_id):

#     """ This function queries a specific match
#         from the database and returns it as json
#         It is annotated with the route Annotation
#         for representing an endpoint of the API
#         Input: match_id: id of the match
#         Return: json of a match
#     """
#     match = Match.query.get_or_404(match_id)
#     return jsonify(match.to_json())


# @api.route('/matches/<int:match_id>/sets', methods=['GET'])
# @permission_required(Permission.SET)
# def get_sets_of_match(match_id):

#     """ This function queries all sets of
#         a specific match from the database and returns it as json
#         It is annotated with the route Annotation
#         for representing an endpoint of the API
#         Input: match_id: id of the match
#         Return: json of sets
#     """
#     sets = [set for set in Set.query.filter_by(match_id=match_id).all()]
#     return jsonify([set.to_json() for set in sets])


# @api.route('/matches/<int:match_id>/sets/<int:set_id>', methods=['GET'])
# @permission_required(Permission.SET)
# def get_set_of_match(match_id, set_id):

#     """ This function queries a specific set of a specific match
#         from the database and returns it as json
#         It is annotated with the route Annotation
#         for representing an endpoint of the API
#         Input: match_id: id of the match
#         Input: set_id: id of the set
#         Return: json of a set
#     """
#     set = Set.query.filter_by(id=set_id, match_id=match_id).one()
#     return jsonify(set.to_json())


# @api.route('/matches/<int:match_id>/sets', methods=['POST'])
# def create_set_of_match(match_id):

#     """ This function gets a set of a specific match as json and
#         makes an entry in the database for that and
#         returns a successful statuscode as response in json
#         It is annotated with the route Annotation for
#         representing an endpoint of the API
#         Input: match_id: id of the match
#         Return: json of 201 statuscode
#     """
#     set = Set.from_json(request.json, match_id)
#     db.session.add(set)
#     db.session.commit()
#     match = Match.query.filter_by(id=match_id).one()
#     tournament = Tournament.query.filter_by(id=match.tournament_id).one()
#     match.finish()
#     if tournament.modus == "KO":
#         if tournament.check_is_phase_finishable():
#             tournament.draw_next_ko_round()
#     else:
#         if tournament.check_is_tournament_finishable():
#             tournament.over = True
#         elif tournament.check_is_phase_finishable():
#             tournament.draw_round()
#     return jsonify(set.to_json()), 201, {'url': url_for('api.get_set_of_match',
#                                          set_id=set.id, match_id=match_id)}


# @api.route('/matches/<int:match_id>/sets/<int:set_id>', methods=['PUT'])
# @permission_required(Permission.SET)
# def update_set_of_match(match_id, set_id):

#     """ This function gets a set of a specific match as json and
#         persists the change in the database.
#         It returns a successful statuscode as response in json
#         It is annotated with the route Annotation
#         for representing an endpoint of the API
#         Input: match_id: id of the match
#         Return: json of 200 statuscode
#     """
#     actual_set = Set.query.filter_by(id=set_id, match_id=match_id).one()
#     posted_set = Set.from_json(request.json)
#     if actual_set is not posted_set:
#         actual_set = posted_set
#         db.session.add(actual_set)
#         db.session.commit()
#     return jsonify(set.to_json()), 200, {'url': url_for('api.get_set_of_match',
#                                          set_id=set.id, match_id=match_id)}
