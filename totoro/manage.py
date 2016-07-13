import os
from flask_script import Manager, Command, Shell
from flask_migrate import Migrate, MigrateCommand
from flask import Flask
from app import create_app, db
from app.models import User, Role, Player, Team, Tournament, Match, Set


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Player=Player, Team=Team, Tournament=Tournament, Match=Match, Set=Set)

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def initdb():
    """Creates the database"""
    pass


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def upgrade():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from app.models import Player, Team

    # migrate database to latest revision
    upgrade()


if __name__ == "__main__":
    manager.run()
