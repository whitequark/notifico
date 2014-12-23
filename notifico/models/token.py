# -*- coding: utf8 -*-
__all__ = (
    'AuthTokenModel',
)
import datetime

from notifico.server import db


class AuthTokenModel(db.Model):
    """
    Service authentication tokens, such as those used for Github's OAuth.
    """
    __tablename__ = 'authtoken'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)
    name = db.Column(db.String(50), nullable=False)
    token = db.Column(db.String(512), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('UserModel', backref=db.backref(
        'tokens', order_by=id, lazy='dynamic', cascade='all, delete-orphan'
    ))

    @classmethod
    def new(cls, token, name):
        c = cls()
        c.token = token
        c.name = name
        return c
