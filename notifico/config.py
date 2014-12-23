###
# General Flask configuration.
###
import datetime

# This key MUST be changed before you make a site public, as it is used
# to sign the secure cookies used for sessions.
SECRET_KEY = 'YouReallyShouldChangeThisYouKnow'

###
# SQLAlchemy configuration.
###
SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'

###
# Flask-Login configuration.
###
REMEMBER_COOKIE_DURATION = datetime.timedelta(days=30)

###
# Flask-debugtoolbar configuration.
###
DEBUG_TB_INTERCEPT_REDIRECTS = False

###
# Flask-WTF
###
# Automatic CSRF support on forms to protect from attacks. It is
# always recommended to leave this on.
CSRF_ENABLED = True

# ###
# Flask-Mail
# ###
# Allows Notifico to send password reset emails and other
# notifications.
# MAIL_SERVER = 'localhost'
# MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = False
# MAIL_USERNAME = None
# MAIL_PASSWORD = None
# DEFAULT_MAIL_SENDER = None

# ###
# Redis Configuration
# ###
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Your Google Analytics ID (ID-XXXXXXX) as a string.
# If left blank, the analytics snippet will not be included in the
# base template.
GOOGLE = None

# Your Sentry (http://getsentry.com) DSN key.
SENTRY_DSN = None

# ###
# Celery Configuration
# ###
CELERY_BROKER_URL = 'redis://'
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_IMPORTS = [
    'notifico.services.background'
]
CELERY_TASK_SERIALIZER = 'json'


# ###
# Misc. Settings
# ###

# Should notifico send password reset emails? This requires
# Flask-Mail to be properly configured.
NOTIFICO_PASSWORD_RESET = False
# How long (in seconds) password resets should be valid for.
NOTIFICO_PASSWORD_RESET_EXPIRY = 60 * 60 * 24
# The address or (name, address) to use when sending an email.
NOTIFICO_MAIL_SENDER = None
