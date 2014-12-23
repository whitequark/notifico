# -*- coding: utf8 -*-
from functools import wraps

from redis import Redis
from celery import Celery
from flask import (
    Flask,
    g,
    redirect,
    url_for
)
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from notifico.util import pretty

db = SQLAlchemy()
sentry = Sentry()
cache = Cache()
mail = Mail()
celery = Celery()


def user_required(f):
    """
    A decorator for views which required a logged in user.
    """
    @wraps(f)
    def _wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('account.login'))
        return f(*args, **kwargs)
    return _wrapped


def group_required(name):
    """
    A decorator for views which required a user to be member
    to a particular group.
    """
    def _wrap(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            if g.user is None or not g.user.in_group(name):
                return redirect(url_for('account.login'))
            return f(*args, **kwargs)
        return _wrapped
    return _wrap


def create_app():
    """
    Construct a new Flask instance and return it.
    """
    app = Flask(__name__, static_url_path='')
    app.config.from_object('notifico.config')

    if not app.debug:
        # If sentry (http://getsentry.com) is configured we should use it
        # when not running in local debugging mode.
        if app.config.get('SENTRY_DSN'):
            sentry.dsn = app.config.get('SENTRY_DSN')
            sentry.init_app(app)

    # Setup our redis connection (which is already thread safe)
    app.redis = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )

    # Attach Flask-Cache to our application instance. We override
    # the backend configuration settings because we only want one
    # Redis instance.
    cache.init_app(app, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': app.redis,
        'CACHE_OPTIONS': {
            'key_prefix': 'cache_'
        }
    })

    # Attach Flask-Mail to our application instance.
    mail.init_app(app)
    # Attach Flask-SQLAlchemy to our application instance.
    db.init_app(app)

    # Update celery's configuration with our application config.
    celery.config_from_object(app.config)

    # Import and register all of our blueprints.
    from notifico.views.account import account
    from notifico.views.public import public
    from notifico.views.projects import projects

    app.register_blueprint(account, url_prefix='/user')
    app.register_blueprint(projects, url_prefix='/projects')
    app.register_blueprint(public)

    # Register our custom error handlers.
    from notifico.views import errors

    app.error_handler_spec[None][500] = errors.error_500

    # cia.vc XML-RPC kludge.
    from notifico.services.hooks.cia import handler
    handler.connect(app, '/RPC2')

    # Setup some custom Jinja2 filters.
    app.jinja_env.filters['pretty_date'] = pretty.pretty_date
    app.jinja_env.filters['plural'] = pretty.plural
    app.jinja_env.filters['fix_link'] = pretty.fix_link

    return app


def create_celery():
    """
    Creates and returns a new celery instance with a Task subclass that will
    wrap all tasks in an application context.
    """
    app = create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    Task = celery.Task

    class ContextTask(Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return Task.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

#: Celery instance for background tasks.
celery = create_celery()
