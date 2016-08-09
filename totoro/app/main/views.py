from flask import render_template, redirect, url_for, flash, g
from flask_login import login_required, current_user
from .. import db
from ..models import User, Player, Team, Tournament, Match, Role
from .forms import PlayerForm, TeamForm, KoTournamentForm
from .forms import TournamentForm, EditProfileForm
from datetime import datetime
from . import main


@main.before_request
def before_request():

    """ This function updates the current user last seen attribut
        into the database with the actual timestamp.
        It is decorated with before_request which means,
        that it is call before each request.
    """
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@main.route('/', methods=['GET', 'POST'])
def index():

    """ This function redirects all requests on the base
        route to the listing of all tournaments.
        Return: Redirection to listing of all tournaments.
    """
    return redirect(url_for('main.list_tournaments'))


@main.route('/user/<username>')
def user(username):

    """ This function renders the profile of a specific user.
        Return: Template of given user
    """
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('list_user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    """ This function renders the profile of a current user.
        Return: Template of given user to edit its profile or
        redirects to the listing of users
    """
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.list_user', username=current_user.username))
    form.name.data = current_user.name
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):

    """ This function renders the profile of a specific user.
        Return: Template of given user to edit its profile or
        redirects to the listing of users
    """
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/players', methods=['GET', 'POST'])
def list_players():

    """ This function returns the rendersing of all players.
        Return: Template of all users
    """
    players = Player.query.all()
    return render_template('list_players.html', players=players)


@main.route('/players/<int:p_id>', methods=['GET', 'POST'])
@login_required
def edit_player(p_id):

    """ This function returns the rendered template of all players.
        Input: p_id - player id
        Return: The template to edit the given user or
        returns listing of all players in submission.
    """
    player = Player.query.get_or_404(p_id)
    form = PlayerForm()
    if form.validate_on_submit():
        player.name = form.name.data
        player.email = form.email.data
        db.session.add(player)
        db.session.commit()
        flash('The player has been updated.')
        return redirect(url_for('.list_players'))
    form.name.data = player.name
    form.email.data = player.email
    return render_template('edit_player.html', form=form)


@main.route('/players/create', methods=['GET', 'POST'])
@login_required
def add_player():
    """ This function returns the rendered template to create a player.
        Return: The template to create a user on submission.
    """
    form = PlayerForm()
    if form.validate_on_submit():
        player = Player.query.filter_by(name=form.name.data).first()
        if player is None:
            player = Player(name=form.name.data, email=form.email.data)
            db.session.add(player)
            db.session.commit()
        return redirect(url_for('.list_players'))
    return render_template('edit_player.html', form=form)


@main.route('/players/del/<int:id>', methods=['GET', 'POST'])
@login_required
def del_player(id):

    """ This function returns the rendered template to delete a player.
        Return: The template of all players.
    """
    player = Player.query.get(id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('.list_players'))


@main.route('/tournaments/<int:tournament_id>/teams/create',
            methods=['GET', 'POST'])
@login_required
def add_team(tournament_id):

    """ This function returns the rendered template
        to create a team out of two players.
        Input: tournament_id id of given tournament
        Return: The template of all players.
    """
    form = TeamForm()
    if form.validate_on_submit():
        team = Team()
        player_a = Player.query.filter_by(id=form.player_a.data.id).first()
        player_b = Player.query.filter_by(id=form.player_b.data.id).first()
        team.players.append(player_a)
        team.players.append(player_b)
        team.tournament_id = tournament_id
        db.session.add(team)
        db.session.commit()
        return redirect(url_for('.list_teams_of_tournament', id=tournament_id))
    return render_template('edit_team.html', form=form)


@main.route('/tournaments/<int:t_id>/teams/<int:team_id>', methods=['GET'])
@login_required
def edit_team(t_id, team_id):

    """ This function returns the rendered template to alter a team.
        Input: tournament_id id of given tournament
        Input: team_id id of given team
        Return: The template to display a team.
    """
    team = Team.query.get_or_404(team_id)
    form = TeamForm()
    if form.validate_on_submit():
        player_a = Player.query.filter_by(id=form.player_a.data.id).first()
        player_b = Player.query.filter_by(id=form.player_b.data.id).first()
        team.players.append(player_a)
        team.players.append(player_b)
        db.session.add(team)
        flash('The team has been updated.')
        db.session.commit()
        return redirect(url_for('.list_teams'))
    return render_template('edit_team.html', form=form, team=team)


@main.route('/tournaments/<int:tournament_id>/teams/del/<int:team_id>',
            methods=['GET', 'POST'])
@login_required
def del_team(tournament_id, team_id):

    """ This function deletes a team and returns a a template
        to display all teams of a tournament.
        Input: tournament_id id of given tournament
        Input: team_id id of given team
        Return: The template to display all team of given tournament.
    """
    team = Team.query.filter_by(id=team_id).one()
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('.list_teams_of_tournament', id=tournament_id))


@main.route('/tournaments', methods=["GET", "POST"])
@login_required
def list_tournaments():

    """ This function returns the rendered template to display all tournaments.
        Return: The template to display all tournaments.
    """
    tournaments = Tournament.query.all()
    return render_template('list_tournaments.html', tournaments=tournaments)


@main.route('/tournaments/create', methods=['GET', 'POST'])
@login_required
def add_tournament():

    """ This function returns the rendered template to create a new tournament.
        Return: The template to create a tournament.
    """
    form = TournamentForm()
    if form.validate_on_submit():
        tournament = Tournament.query.filter_by(name=form.name.data).first()
        if tournament is None:
            tournament = Tournament()
            tournament.name = form.name.data
            tournament.modus = form.modus.data
            tournament.max_phase = form.max_phase.data
            tournament.set_count = form.set_count.data
            db.session.add(tournament)
            db.session.commit()
        return redirect(url_for('.list_tournaments'))
    return render_template('edit_tournament.html', form=form)


@main.route('/tournaments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tournament(id):

    """ This function returns the rendered template to alter the given tournament.
        Input: id - id of the given tournament
        Return: The template to alter the given tournament.
    """
    tournament = Tournament.query.get_or_404(id)
    form = TournamentForm()
    if form.validate_on_submit():
        if tournament is None:
            tournament = Tournament()
            tournament.name = form.name.data
            tournament.modus = form.modus.data
            tournament.max_phase = form.max_phase.data
            tournament.set_count = form.set_count.data
            db.session.add(tournament)
            flash('The tournament has been updated.')
            db.session.commit()
        return redirect(url_for('.list_tournaments'))
    form.name.data = tournament.name
    form.modus.data = tournament.modus
    form.max_phase.data = tournament.max_phase
    form.set_count.data = tournament.set_count
    return render_template('edit_tournament.html', form=form)


@main.route('/tournaments/del/<int:id>', methods=['GET', 'POST'])
@login_required
def del_tournament(id):

    """ This function deletes a given tournament.
        Input: id - id of the given tournament
        Return: Redirect to listings of tournaments.
    """
    tournament = Tournament.query.get(id)
    db.session.delete(tournament)
    db.session.commit()
    return redirect(url_for('.list_tournaments'))


@main.route('/tournaments/start/<int:id>')
@login_required
def start_tournament(id):

    """ This function starts the given tournament.
        Input: id - id of the given tournament
        Return: Redirect to listings of tournaments
    """

    tournament = Tournament.query.filter_by(id=id).one()
    matches = Match.query.filter_by(tournament_id=id)

    if not tournament.over and not matches.first():
        if tournament.modus == "Swiss":
            tournament.shuffle_initial_ranking()
            tournament.draw_round()
        else:
            if tournament.modus == "KO" and tournament.parent is None:
                tournament.set_initial_ko_matches()
            else:
                tournament.set_initial_ko_ranking()
                tournament.set_initial_ko_matches()
    else:
        flash("Tournament has already started!")
    return redirect(url_for('.list_tournaments'))


@main.route('/tournaments/<int:id>/teams', methods=['GET', 'POST'])
@login_required
def list_teams_of_tournament(id):

    """ This function lists all teams of a given tournament.
        And also has a form for adding teams to the tournament.
        Input: id - id of the given tournament
        Return: The template to list all tournaments.
    """
    form = TeamForm()
    teams = Team.query.filter_by(tournament_id=id)
    players = Player.query.all()

    if form.validate_on_submit():
        team = Team()
        team.tournament_id = id
        player_a = Player.query.filter_by(id=form.player_a.data.id).first()
        player_b = Player.query.filter_by(id=form.player_b.data.id).first()

        if not any(team.check_if_player_in_team(player_a) for team in teams or
                   any(team.check_if_player_in_team(player_b)
                       for team in teams)):
            team.players.extend([player_a, player_b])
            db.session.add(team)
            flash('The tournament has been updated.')
            db.session.commit()
            return redirect(url_for('.list_teams_of_tournament', id=id))
        else:
            flash("One of these players are already" +
                  " playing in that tournament!")
    return render_template('list_teams_of_tournament.html',
                           form=form, teams=teams, players=players,
                           tournament_id=id)


@main.route('/tournaments/<int:id>/ko', methods=['GET', 'POST'])
@login_required
def create_ko_for_finished_tournament(id):

    """ This function enables out of a fnished tournament
        a knock-out tournament.
        Input: id - id of the given tournament
        Return: The template to edit the given tournament.
    """
    form = KoTournamentForm()
    tournament = Tournament()
    old_tournament = Tournament.query.filter_by(id=id).one()
    form.name.data = old_tournament.name + "- KO"
    form.modus.data = "KO"
    if form.validate_on_submit():
        tournament.max_phase = 0
        tournament.name = form.name.data
        tournament.modus = form.modus.data
        tournament.set_count = form.set_count.data
        tournament.get_teams_from_other_tournament(old_tournament.teams)
        tournament.parent = old_tournament.id
        return redirect(url_for('.list_tournaments'))
    return render_template('edit_tournament.html',
                           form=form, tournament=tournament)


@main.route("/tournaments/<int:id>/phases")
@login_required
def list_phases_of_tournament(id):

    """ This function displays the rounds of a given tournament.
        Input: id - id of the given tournament
        Return: The template to display the rounds of a given tournament.
    """

    matches = Match.query.filter_by(tournament_id=id)
    teams = Team.query
    if matches:
        tournament = Tournament.query.filter_by(id=id).first()
        if tournament.modus == "KO":
            phases = tournament.get_matches_structured_in_ko()
        else:
            phases = tournament.get_matches_structured_in_phases()
    else:
        flash("Tournament has not started!")
        return redirect(url_for('.list_tournaments'))
    return render_template('list_phases_of_tournament.html',
                           tournament=tournament, phases=phases, teams=teams)
