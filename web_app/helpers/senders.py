from ..extensions import ext_mail
from . import generate_token

from database import models

import requests
from flask_mail import Message
from flask import current_app

from flask import flash, url_for, render_template, g
import os


def send_confirmation(user):
    """Send a confirmation email to user to verify his email"""
    token = generate_token(user.email)
    confirm_url = url_for('.confirm_email', token=token, _external=True)
    html = render_template('account/emails/activate.pug',
                           confirm_url=confirm_url)
    subject = "Please confirm your email"
    if send_email(user.email, subject, html):
        flash("A confirmation email has been sent via email.", "info")

    t = models.Token(user.id, token)

    g.session.add(t)
    g.session.commit()


def send_reset_link(user):
    """Send reset link to user to reset his password"""
    token = generate_token(user.id)
    reset_url = url_for('.change', token=token, _external=True)
    html = render_template('account/emails/reset.pug', reset_url=reset_url)
    subject = "Password Reset Request"
    if send_email(user.email, subject, html):
        flash("An email has been sent. Check your Inbox.", "info")

    t = models.Token(user.id, token)
    g.session.add(t)
    g.session.commit()


def send_email_mailgun(to_address, subject, html):
    """Send an email to the given address with mailgun api

    Args:
        to_address (str): Email address of the recipient.
        subject (str): Message subject.
        html (str): Body (HTML version) of the message.

    Returns:
        boolean: Request status.
    """
    try:
        r = requests. \
            post("https://api.mailgun.net/v3/%s/messages" % current_app.config['MAILGUN_DOMAIN'],
                 auth=("api", current_app.config['MAILGUN_KEY']),
                 data={
                     "from": current_app.config['MAIL_DEFAULT_SENDER'],
                     "to": to_address,
                     "subject": subject,
                     "html": html
            }
            )
        return r.status_code == 200
    except Exception as e:
        flash(e, "error")
        return False


def send_email(to, subject, template):
    """Send an email to the given address

    If the environment is production the email will be sent using mailgun api, 
    otherwise gmail SMTP is used.

    Args:
        to (str): Email address of the recipient.
        subject (str): Message subject.
        template (str): Body (HTML version) of the message.

    Returns:
        boolean: Request status.
    """
    if os.environ.get('APP_ENV', 'development') == 'production':
        return send_email_mailgun(to, subject, template)
    else:
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        try:
            with current_app.app_context():
                ext_mail.send(msg)
            return True
        except Exception as e:
            print(e)
            flash(
                "Something went wrong and we couldn't send you an email! Please try again later.", "error")
        return False
