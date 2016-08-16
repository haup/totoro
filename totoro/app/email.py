from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail

# This package is taken from the https://github.com/miguelgrinberg/flasky,
# its mail implementation for a flask application fits
# every aspect for building a valid prototype.


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['TOTORO_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['TOTORO_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
