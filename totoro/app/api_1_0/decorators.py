from functools import wraps
from flask import g
from .errors import forbidden


def permission_required(permission):

    """ This decorator lets only call the user a specific function
        if the user is logged in.
        Input: permission: object of permission enumeration
        Output: decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
