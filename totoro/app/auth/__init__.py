from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views

# This package is taken from the https://github.com/miguelgrinberg/flasky,
# its authentification implementation for a flask application fits
# every aspect for building a valid prototype. It may vary minimal postitions.
