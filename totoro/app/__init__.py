from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


# This package is the app package of the prototype flask application totoro.
# It was formed during the developing due to bachelor thesis by Tim Unkrig.

# Its based by the book by Miguel Grinberg 'Flask Web Development'
# with the ISBN: 978-1-449-37262-0

# This application is there to conduct a foosbal tournament
# according to the ruleset of the ITSF
# (International Table Soccer Foundation)
# Therefor a Flask application was build with a REST API to connect
# an android client to enter results with the app.


def create_app(config_name):

    """ This function creates the application and initializes the components"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    config[config_name].init_app(app)
    db.init_app(app)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app
