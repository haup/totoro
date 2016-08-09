from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(403)
def forbidden(e):

    """ This function is called if there was a 403 error exception
        and displays the related error page
        Return: template of 403 error page
    """
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    """ This function is called if there was a 404 error exception
        and displays the related error page
        Return: template of 404 error page
    """
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):

    """ This function is called if there was a 404 error exception
        and displays the related error page
        Return: template of 404 error page
    """
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
