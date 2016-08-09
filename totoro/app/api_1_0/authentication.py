from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):

    """ This function gets email address or a token
        of an user and the user´s password and
        verfifies its correctness
        Input: email_or_token, password
        Output: user - verfified user
    """
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():

    """ This function returns a json with the error message 401,
        if the user typed in invalid credentials
        The function is decorated as the error handler for the auth blueprints
        Output: json with 401 and invalid credentials
    """
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():

    """ This function checks if the current user is allowed to
        acces the api before the api gets requested.
        Output: json with 403 status code and message Unconfirmed account
    """
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():

    """ This function returns a valid token to
        access the api without using the user´s password
        Output: json with a valid token to access the api within one hour.
    """
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
                    expiration=3600), 'expiration': 3600})
