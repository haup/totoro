from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask_login import login_required, current_user
from .. import db
from ..models import User, Player, Team, Tournament
from . import main
from .forms import NameForm, PlayerForm, TeamForm, TournamentForm, EditProfileForm, EditProfileAdminForm, SearchForm
from datetime import datetime


@main.before_request
def before_request():
    user = current_user
    if user.is_authenticated:
        user.last_seen = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        user.search_form = SearchForm()

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    return render_template('index.html', form=form)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
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
    players = Player.query.all()
    return render_template('players.html', players=players)


@main.route('/players/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_player(id):
    player = Player.query.get_or_404(id)
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
    player = Player.query.get(id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('.list_players'))


@main.route('/teams', methods=['GET', 'POST'])
@login_required
def list_teams():
    teams = Team.query.all()
    players = Player.query.all()
    return render_template('teams.html', teams=teams, players=players)


@main.route('/teams/create', methods=['GET', 'POST'])
@login_required
def add_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team()
        player_a = Player.query.filter_by(id=form.player_a.data.id).first()
        player_b = Player.query.filter_by(id=form.player_b.data.id).first()
        team.players.append(player_a)
        team.players.append(player_b)
        db.session.add(team)
        db.session.commit()
        return redirect(url_for('.list_teams'))
    return render_template('edit_team.html', form=form)


@main.route('/teams/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_team(id):
    team = Team.query.get_or_404(id)
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

@main.route('/teams/del/<int:id>', methods=['GET', 'POST'])
@login_required
def del_team(id):
    team = Team.query.get(id)
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('.list_teams'))


@main.route('/tournaments', methods=["GET", "POST"])
@login_required
def list_tournaments():
    tournaments = Tournament.query.all()
    return render_template('tournaments.html', tournaments=tournaments)


@main.route('/tournaments/create', methods=['GET', 'POST'])
@login_required
def add_tournament():
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
    tournament = Tournament.query.get(id)
    db.session.delete(tournament)
    db.session.commit()
    return redirect(url_for('.list_tournaments'))

@main.route('/tournaments/start/<int:id>')
@login_required
def start_tournament():
    pass