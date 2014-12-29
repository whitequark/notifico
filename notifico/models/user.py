# -*- coding: utf8 -*-
__all__ = ('UserModel', 'GroupModel')
import os
import base64
import hashlib
import datetime

from werkzeug import security
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from notifico.server import db
from notifico.models import CaseInsensitiveComparator


class UserModel(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)

    # ---
    # Required Fields
    # ---
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(8), nullable=False)
    joined = db.Column(db.TIMESTAMP(), default=datetime.datetime.utcnow)

    # ---
    # Public Profile Fields
    # ---
    company = db.Column(db.String(255))
    website = db.Column(db.String(255))
    location = db.Column(db.String(255))

    @classmethod
    def new(cls, username, email, password):
        u = cls()
        u.email = email.lower().strip()
        u.salt = cls._create_salt()
        u.password = cls._hash_password(password, u.salt)
        u.username = username.strip()
        return u

    @staticmethod
    def _create_salt():
        """
        Returns a new base64 salt.
        """
        return base64.b64encode(os.urandom(8))[:8]

    @staticmethod
    def _hash_password(password, salt):
        """
        Returns a hashed password from `password` and `salt`.
        """
        return hashlib.sha256(salt + password.strip()).hexdigest()

    def set_password(self, new_password):
        self.salt = self._create_salt()
        self.password = self._hash_password(new_password, self.salt)

    def in_group(self, name):
        """
        Returns ``True`` if this user is in the group `name`, otherwise
        ``False``.
        """
        return any(g.name == name.lower() for g in self.groups)

    def add_group(self, name):
        """
        Adds this user to the group `name` if not already in it. The group
        will be created if needed.
        """
        if self.in_group(name):
            # We're already in this group.
            return

        self.groups.append(GroupModel.get_or_create(name=name))

    def __repr__(self):
        return u'<User {u.username}>'.format(u=self)

    @hybrid_property
    def username_i(self):
        return self.username.lower()

    @username_i.comparator
    def username_i(cls):
        return CaseInsensitiveComparator(cls.username)

    @classmethod
    def by_username(cls, username):
        """
        Lookup a user by their username (case insensitive).

        :rtype: :class:`UserModel` or `None`.
        """
        return cls.query.filter(cls.username_i == username).first()

    def check_password(self, password):
        """
        Compare `password` to the hashed and salted password for this user.

        :returns: `True` or `False`.
        :rtype: bool
        """
        if self.salt is not None:
            # A legacy password.
            return self._hash_password(password, self.salt) == self.password

        # A modern password.
        return security.check_password_hash(self.password, password)


class GroupModel(db.Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), unique=True, nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('UserModel', backref=db.backref(
        'groups', order_by=id, lazy='joined'
    ))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Group({name!r})>'.format(name=self.name)

    @classmethod
    def get_or_create(cls, name):
        name = name.lower()

        g = cls.query.filter_by(name=name).first()
        if not g:
            g = GroupModel(name=name)

        return g
