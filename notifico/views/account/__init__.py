# -*- coding: utf-8 -*-
from flask import (
    Blueprint,
    render_template,
    redirect,
    current_app,
    url_for,
    session,
    request,
    flash
)
from flask.ext import login
from flask.ext.login import current_user, login_required
from wtforms import validators

from notifico.server import db
from notifico.models import UserModel
from notifico.services import reset, background
from notifico.views.account.forms import (
    UserLoginForm,
    UserRegisterForm,
    UserDeleteForm,
    UserForgotForm,
    UserResetForm,
    UserPasswordForm
)

account = Blueprint('account', __name__, template_folder='templates')


@account.route('/login', methods=['GET', 'POST'])
def login_view():
    """
    Standard login form.
    """
    if current_user.is_authenticated():
        return redirect(url_for('public.landing'))

    form = UserLoginForm()
    if form.validate_on_submit():
        user = UserModel.by_username(form.username.data)
        if not user:
            form.username.errors.append(validators.ValidationError(
                'Not a valid username and/or password.'
            ))
        elif user.check_password(form.password.data):
            login.login_user(user)
            return redirect('/')
        else:
            form.username.errors.append(validators.ValidationError(
                'Not a valid username and/or password.'
            ))

    return render_template('login.html', form=form)


@account.route('/logout')
@login_required
def logout():
    """
    Logout the current user.
    """
    login.logout_user()
    return redirect(url_for('.login_view'))


@account.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    """
    If NOTIFICO_PASSWORD_RESET is enabled and Flask-Mail is configured,
    this view allows you to request a password reset email. It also
    handles accepting those tokens.
    """
    # Because this functionality depends on Flask-Mail and
    # celery being properly configured, we default to disabled.
    if not current_app.config.get('NOTIFICO_PASSWORD_RESET'):
        flash(
            'Password resets have been disabled by the administrator.',
            category='warning'
        )
        return redirect('.login')

    # How long should reset tokens last? We default
    # to 24 hours.
    token_expiry = current_app.config.get(
        'NOTIFICO_PASSWORD_RESET_EXPIRY',
        60 * 60 * 24
    )

    form = UserForgotForm()
    if form.validate_on_submit():
        user = UserModel.by_username(form.username.data)
        new_token = reset.add_token(user, expire=token_expiry)

        # Send the email as a background job so we don't block
        # up the browser (and to use celery's built-in rate
        # limiting).
        background.send_mail.delay(
            'Notifico - Password Reset for {username}'.format(
                username=user.username
            ),
            # We're already using Jinja2, so we might as well use
            # it to render our email templates as well.
            html=render_template(
                'email_reset.html',
                user=user,
                reset_link=url_for(
                    '.reset_password',
                    token=new_token,
                    uid=user.id,
                    _external=True
                ),
                hours=token_expiry / 60 / 60
            ),
            recipients=[user.email],
            sender=current_app.config['NOTIFICO_MAIL_SENDER']
        )
        flash('A reset email has been sent.', category='success')
        return redirect(url_for('.login'))

    return render_template('forgot.html', form=form)


@account.route('/reset')
def reset_password():
    """
    Endpoint for password reset emails, which validates the token
    and UID pair, then redirects to the password set form.
    """
    token = request.args.get('token')
    uid = request.args.get('uid')

    u = UserModel.query.get(int(uid))
    if not u or not reset.valid_token(u, token):
        flash('Your reset request is invalid or expired.', category='warning')
        return redirect(url_for('.login'))

    session['reset_token'] = token
    session['reset_user_id'] = uid

    return redirect(url_for('.reset_pick_password'))


@account.route('/reset/password', methods=['GET', 'POST'])
def reset_pick_password():
    token = session.get('reset_token')
    user_id = session.get('reset_user_id')

    if not token or not user_id:
        return redirect(url_for('.login'))

    u = UserModel.query.get(int(user_id))
    if not u or not reset.valid_token(u, token):
        flash(
            'Your reset request is invalid or expired.',
            category='warning'
        )
        return redirect(url_for('.login'))

    form = UserResetForm()
    if form.validate_on_submit():
        u.set_password(form.password.data)
        db.session.commit()

        # The user has successfully reset their password,
        # so we want to clean up any other reset tokens as
        # well as our stashed session token.
        reset.clear_tokens(u)
        session.pop('reset_token', None)
        session.pop('reset_user_id', None)

        flash(
            'The password for {username} has been reset.'.format(
                username=u.username
            ),
            category='success'
        )
        return redirect(url_for('.login'))

    return render_template('reset.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
def register():
    """
    If new user registrations are enabled, provides a registration form
    and validation.
    """
    if current_user:
        return redirect(url_for('public.landing'))

    # Make sure this instance is allowing new users.
    if not current_app.config.get('NOTIFICO_NEW_USERS', True):
        return redirect(url_for('public.landing'))

    form = UserRegisterForm()
    if form.validate_on_submit():
        # Checks out, go ahead and create our new user.
        u = UserModel.new(
            form.username.data,
            form.email.data,
            form.password.data
        )
        db.session.add(u)
        db.session.commit()
        # ... and send them back to the login screen.
        return redirect(url_for('.login'))

    return render_template('register.html', form=form)


@account.route('/settings', methods=['GET', 'POST'])
@account.route('/settings/<do>', methods=['GET', 'POST'])
@login_required
def settings(do=None):
    """
    Provides forms allowing a user to change various settings.
    """
    password_form = UserPasswordForm()
    delete_form = UserDeleteForm()

    if do == 'p' and password_form.validate_on_submit():
        # Change the users password.
        current_user.set_password(password_form.password.data)
        db.session.commit()
        flash('Your password has been updated.', category='success')
        return redirect(url_for('.settings'))
    elif do == 'd' and delete_form.validate_on_submit():
        # Delete this users account and all related data.
        # Clear the session.
        if '_u' in session:
            del session['_u']
        if '_ue' in session:
            del session['_ue']
        # Remove the user from the DB.
        current_user.projects.order_by(False).delete()
        db.session.delete(current_user)
        db.session.commit()

        return redirect(url_for('.login'))

    return render_template(
        'settings.html',
        password_form=password_form,
        delete_form=delete_form
    )
