import unittest
from flask import current_app
from app import create_app, db
from app.models import Player, Team, Tournament, Match, Set

class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_create_player(self):
        player = Player(id=1, name='Tim', email='tunkrig@posteo.de')
        db.session.add(player)
        db.session.commit()
        print(player)
        return_player = Player.query.filter_by(name='Tim').one()
        print(return_player)
        self.assertTrue(player is return_player)

    def test_compare_player_with_wrong_request(self):
        player = Player(id=1, name='Tim', email='tunkrig@posteo.de')
        db.session.add(player)
        db.session.commit()
        print(player)
        return_player = Player.query.filter_by(name='test').first()
        print(return_player)
        self.assertFalse(player is return_player)


    def test_create_team(self):
        player_a = Player(name='Test', email='test1@test.de')
        player_b = Player(name='Test2', email='test2@test.de')
        team = Team(id=1, points=0.0, buchholz1=0.0, buchholz2=0.0, ranking=0)
        team.players.append(player_a)
        team.players.append(player_b)
        db.session.add(team)
        db.session.commit()
        db_team = Team.query.filter_by(id=1).one()
        self.assertTrue(team is db_team)

    def test_compare_team_with_wrong_request(self):
        player_a = Player(name='Test', email='test1@test.de')
        player_b = Player(name='Test2', email='test2@test.de')
        team = Team(id=1, points=0.0, buchholz1=0.0, buchholz2=0.0, ranking=0)
        team.players.append(player_a)
        team.players.append(player_b)
        db.session.add(team)
        db.session.commit()
        db_team = Team.query.filter_by(id=45).first()
        self.assertFalse(team is db_team)

    def test_create_tournament(self):
        tournament = Tournament(id=1, name='testTournament', modus='Swiss')
        db.session.add(tournament)
        db.session.commit()
        db_tournament = Tournament.query.filter_by(id=1).one()
        self.assertTrue(tournament is db_tournament)

    def test_compare_tournament_with_wrong_test(self):
        tournament = Tournament(id=1, name='testTournament', modus='Swiss')
        db.session.add(tournament)
        db.session.commit()
        db_tournament = Tournament.query.filter_by(id=9).first()
        self.assertFalse(tournament is db_tournament)

    def test_create_match(self):
        player_a_1 = Player(name='Test', email='test1@test.de')
        player_b_1 = Player(name='Test2', email='test2@test.de')
        player_a_2 = Player(name='Test3', email='test3@test.de')
        player_b_2 = Player(name='Test4', email='test4@test.de')
        team_a = Team()
        team_b = Team()
        team_a.players.append(player_a_1)
        team_a.players.append(player_b_1)
        team_b.players.append(player_a_2)
        team_b.players.append(player_b_2)
        db.session.add(team_a, team_b)
        db.session.commit()
        match = Match(id=1)
        db.session.add(match)
        db.session.commit()
        db_match = Match.query.filter_by(id=1).one()
        self.assertTrue(match is db_match)

    def test_compare_match_with_wrong_request(self):
        player_a_1 = Player(name='Test', email='test1@test.de')
        player_b_1 = Player(name='Test2', email='test2@test.de')
        player_a_2 = Player(name='Test3', email='test3@test.de')
        player_b_2 = Player(name='Test4', email='test4@test.de')
        team_a = Team()
        team_b = Team()
        team_a.players.append(player_a_1)
        team_a.players.append(player_b_1)
        team_b.players.append(player_a_2)
        team_b.players.append(player_b_2)
        db.session.add(team_a, team_b)
        db.session.commit()
        match = Match(id=1)
        db.session.add(match)
        db.session.commit()
        db_match = Match.query.filter_by(id=42).first()
        self.assertFalse(match is db_match)

    def test_create_set(self):
        player_a_1 = Player(name='Test', email='test1@test.de')
        player_b_1 = Player(name='Test2', email='test2@test.de')
        player_a_2 = Player(name='Test3', email='test3@test.de')
        player_b_2 = Player(name='Test4', email='test4@test.de')
        team_a = Team()
        team_b = Team()
        team_a.players.append(player_a_1)
        team_a.players.append(player_b_1)
        team_b.players.append(player_a_2)
        team_b.players.append(player_b_2)
        db.session.add(team_a, team_b)
        match = Match(id=1)
        set = Set(score_a=5, score_b=3, match_id=1)
        match.sets.append(set)
        db.session.add(match)
        db.session.commit()
        self.assertTrue(set in match.sets)

    def test_compare_set_with_wrong_request(self):
        wrong_set = Set(score_b=5, score_a=3)
        match = Match(id=1)
        set = Set(score_a=5, score_b=3, match_id=1)
        match.sets.append(set)
        db.session.add(match)
        self.assertFalse(wrong_set in match.sets)
