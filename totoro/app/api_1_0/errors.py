from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message):

    """ This function gets a message for the statuscode 400
        and returns it as json
        Input: message String of the given message
        Output: json of message and statuscode
    """
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):

    """ This function gets a message for the statuscode 401
        and returns it as json
        Input: message: string of the given message
        Output: json of message and statuscode
    """
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):

    """ This function gets a message for the statuscode 403
        and returns it as json
        Input: message string of the given message
        Output: json of message and statuscode
    """
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):

    """ This function gets an exception as input and wraps it
        as the message of a bad reqeust and returns it as json
        Input: exception e
        Output: json of message and statuscode
    """
    return bad_request(e.args[0])
