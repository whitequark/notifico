# -*- coding: utf-8 -*-
from flask.ext.mail import Message

from notifico.server import celery, mail


@celery.task
def send_mail(*args, **kwargs):
    """
    Sends an email using Flask-Mail and Notifico's configuration
    settings.
    """
    # TODO: Allow bulk sending using flask.mail.Connection.
    m = Message(*args, **kwargs)
    mail.send(m)
