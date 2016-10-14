import os

basedir = os.path.abspath(os.path.dirname(__file__))

SMTM_CLIENT = os.environ['SMTM_CLIENT']

OAUTH_API = os.environ['OAUTH_API']
OAUTH_CLIENT_ID = os.environ['OAUTH_CLIENT_ID']
OAUTH_CLIENT_SECRET = os.environ['OAUTH_CLIENT_SECRET']

COOKIE_KEY_ACCESS_TOKEN = 'mat'
COOKIE_KEY_USER_DATA = 'ud'

# flask
SECRET_KEY = os.environ['SECRET_KEY']

TEMPLATES_AUTO_RELOAD = True
