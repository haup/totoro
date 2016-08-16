from flask import jsonify, request, url_for
from . import api
from .. import db
from .decorators import permission_required
from ..models import Tournament, Team, Permission, Match, Set


@api.route('/tournaments')
@permission_required(Permission.SET)
def get_tournaments():
    """ This function queries all tournaments
        from the database and returns it as json
        It is annotated with the route Decorator
        for representing an endpoint of the API
        Return: json of tournaments
    """
    tournaments = Tournament.query.all()
    return jsonify([tournament.to_json() for tournament in tournaments])


@api.route('/tournaments/<int:id>')
@permission_required(Permission.SET)
def get_tournament(id):
    """ This function queries a specific tournament
        from the database and returns it as json
        It is annotated with the route Decorator
        for representing an endpoint of the API
        Return: json of tournament
    """
    tournament = Tournament.query.get_or_404(id)
    return jsonify(tournament.to_json())


@api.route('/tournaments/<int:id>/teams', methods=['GET'])
@permission_required(Permission.SET)
def get_teams_of_tournaments(id):
    """ This function queries all teams of a specific tournament
        from the database and returns it as json
        It is annotated with the route Decorator
        for representing an endpoint of the API
        Return: json of teams
    """
    teams = Team.query.filter_by(tournament_id=id)
    return jsonify([team.to_json() for team in teams])


@api.route('/tournaments/<int:tournament_id>/teams/<int:team_id>')
@permission_required(Permission.SET)
def get_team_of_tournament(tournament_id, team_id):
    """ This function queries a specific team of a specific tournament
        from the database and returns it as json
        It is annotated with the route Decorator
        for representing an endpoint of the API
        Return: json of team
    """
    team = Team.query.filter_by(id=team_id).one()
    return jsonify(team.to_json())


@api.route('/tournaments/<int:tournament_id>/matches', methods=['GET'])
@permission_required(Permission.SET)
def get_matches(tournament_id):
    """ This function queries all matches from the database and returns it as json
        It is annotated with the route decorator for
        representing an endpoint of the API
        Return: json of matches
    """
    matches = Match.query.filter_by(tournament_id=tournament_id).all()
    return jsonify([match.to_json() for match in matches])


@api.route('/tournaments/<int:tournament_id>/matches/<int:match_id>', methods=['GET'])
@permission_required(Permission.SET)
def get_match(tournament_id, match_id):
    """ This function queries a specific match
        from the database and returns it as json
        It is annotated with the route Annotation
        for representing an endpoint of the API
        Input: match_id: id of the match
        Return: json of a match
    """
    match = Match.query.get_or_404(match_id)
    return jsonify(match.to_json())


@api.route('/tournaments/<int:tournament_id>/matches/<int:match_id>/sets', methods=['GET'])
@permission_required(Permission.SET)
def get_sets_of_match(tournament_id, match_id):
    """ This function queries all sets of
        a specific match from the database and returns it as json
        It is annotated with the route Annotation
        for representing an endpoint of the API
        Input: match_id: id of the match
        Return: json of sets
    """
    sets = [set for set in Set.query.filter_by(match_id=match_id).all()]
    return jsonify([set.to_json() for set in sets])


@api.route('/tournaments/<int:tournament_id>/matches/<int:match_id>/sets/<int:set_id>', methods=['GET'])
@permission_required(Permission.SET)
def get_set_of_match(tournament_id, match_id, set_id):
    """ This function queries a specific set of a specific match
        from the database and returns it as json
        It is annotated with the route Annotation
        for representing an endpoint of the API
        Input: match_id: id of the match
        Input: set_id: id of the set
        Return: json of a set
    """
    set = Set.query.filter_by(id=set_id, match_id=match_id).first()
    return jsonify(set.to_json())


@api.route('/tournaments/<int:tournament_id>/matches/<int:match_id>/sets', methods=['POST'])
def create_set_of_match(tournament_id, match_id):
    """ This function gets a set of a specific match as json and
        makes an entry in the database for that and
        returns a successful statuscode as response in json
        It is annotated with the route Annotation for
        representing an endpoint of the API
        Input: match_id: id of the match
        Return: json of 201 statuscode
    """
    set = Set.from_json(request.json, match_id)
    db.session.add(set)
    db.session.commit()
    match = Match.query.filter_by(id=match_id).one()
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    match.finish()
    if tournament.modus == 'KO':
        if tournament.check_is_phase_finishable():
            tournament.draw_next_ko_round()
    else:
        if tournament.check_is_tournament_finishable():
            tournament.over = True
        elif tournament.check_is_phase_finishableshable():
            tournament.draw_round()
    return jsonify(set.to_json()), 201, {'url': url_for('api.get_set_of_match',
                                                        tournament_id=tournament_id, set_id=set.id,
                                                        match_id=match_id)}


@api.route('/tournaments/<int:tournament_id>/matches/<int:match_id>/sets/<int:set_id>', methods=['PUT'])
@permission_required(Permission.SET)
def update_set_of_match(tournament_id, match_id, set_id):
    """ This function gets a set of a specific match as json and
        persists the change in the database.
        It returns a successful statuscode as response in json
        It is annotated with the route Annotation
        for representing an endpoint of the API
        Input: match_id: id of the match
        Return: json of 200 statuscode
    """
    actual_set = Set.query.filter_by(id=set_id, match_id=match_id).one()
    posted_set = Set.from_json(request.json)
    if actual_set is not posted_set:
        actual_set = posted_set
        db.session.add(actual_set)
        db.session.commit()
    return jsonify(set.to_json()), 200, {'url': url_for('api.get_set_of_match',
                                                        set_id=set.id, match_id=match_id)}
