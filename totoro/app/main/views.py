from flask import render_template, session, redirect, url_for, current_app, flash
from .. import db
from ..models import User, Player, Team, Tournament
from . import main
from .forms import NameForm, PlayerForm, TeamForm, TournamentForm
from datetime import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    return render_template('index.html', form=form)


@main.route('/players', methods=['GET', 'POST'])
def list_players():
    players = Player.query.all()
    return render_template('players.html', players=players)


@main.route('/players/<int:id>', methods=['GET', 'POST'])
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
def del_player(id):
    player = Player.query.get(id)
    db.session.delete(player)
    db.session.commit()
    return redirect(url_for('.list_players'))


@main.route('/teams', methods=['GET', 'POST'])
def list_teams():
    teams = Team.query.all()
    players = Player.query.all()
    return render_template('teams.html', teams=teams, players=players)


@main.route('/teams/create', methods=['GET', 'POST'])
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
def del_team(id):
    team = Team.query.get(id)
    db.session.delete(team)
    db.session.commit()
    return redirect(url_for('.list_teams'))


@main.route('/tournaments', methods=["GET", "POST"])
def list_tournaments():
    tournaments = Tournament.query.all()
    return render_template('tournaments.html', tournaments=tournaments)


@main.route('/tournaments/create', methods=['GET', 'POST'])
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
def del_tournament(id):
    tournament = Tournament.query.get(id)
    db.session.delete(tournament)
    db.session.commit()
    return redirect(url_for('.list_tournaments'))

@main.route('/tournaments/start/<int:id>')
def start_tournament():
    pass