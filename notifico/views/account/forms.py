# -*- coding: utf-8 -*-
from flask.ext import wtf
from flask.ext.login import current_user

from notifico.models import UserModel
from notifico.services import reset


class UserRegisterForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required(),
        wtf.Length(min=2, max=50),
        wtf.Regexp('^[a-zA-Z0-9_]*$', message=(
            'Username must only contain a to z, 0 to 9, and underscores.'
        ))
    ], description=(
        'Your username is public and used as part of your project name.'
    ))
    email = wtf.TextField('Email', validators=[
        wtf.Required(),
        wtf.validators.Email()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required(),
        wtf.Length(5),
        wtf.EqualTo('confirm', 'Passwords do not match.'),
    ])
    confirm = wtf.PasswordField('Confirm Password')

    def validate_username(form, field):
        from notifico.views.account import _reserved

        username = field.data.strip().lower()
        if username in _reserved or UserModel.username_exists(username):
            raise wtf.ValidationError(
                'Sorry, but that username is taken.'
            )


class UserLoginForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required()
    ])
    remember_me = wtf.BooleanField('remember me', description=(
        # TODO: Is there a clean way of doing this dynamically based on
        # the timedelta stored in REMEMBER_COOKIE_DURATION?
        'Remember me on this computer for 30 days.'
    ))


class UserPasswordForm(wtf.Form):
    old = wtf.PasswordField('Old Password', validators=[
        wtf.Required()
    ])
    password = wtf.PasswordField('Password', validators=[
        wtf.Required(),
        wtf.Length(5),
        wtf.EqualTo('confirm', 'Passwords do not match.'),
    ])
    confirm = wtf.PasswordField('Confirm Password')

    def validate_old(form, field):
        if not current_user.check_password(field.data):
            raise wtf.ValidationError('Old Password is incorrect.')


class UserDeleteForm(wtf.Form):
    password = wtf.PasswordField('Password', validators=[
        wtf.Required(),
        wtf.Length(5),
        wtf.EqualTo('confirm', 'Passwords do not match.'),
    ])
    confirm = wtf.PasswordField('Confirm Password')

    def validate_password(form, field):
        if not UserModel.login(current_user.username, field.data):
            raise wtf.ValidationError('Password is incorrect.')


class UserForgotForm(wtf.Form):
    username = wtf.TextField('Username', validators=[
        wtf.Required()
    ])

    def validate_username(form, field):
        user = UserModel.by_username(field.data)
        if not user:
            raise wtf.ValidationError('No such user exists.')

        if reset.count_tokens(user) >= 5:
            raise wtf.ValidationError(
                'You may not reset your password more than 5 times'
                ' in one day.'
            )


class UserResetForm(wtf.Form):
    password = wtf.PasswordField('New Password', validators=[
        wtf.Required(),
        wtf.Length(5),
        wtf.EqualTo('confirm', 'Passwords do not match.'),
    ])
    confirm = wtf.PasswordField('Confirm Password')
