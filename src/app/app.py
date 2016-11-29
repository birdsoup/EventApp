from flask import Flask

import config as C
from database import db
from login_manager import lm
from hasher import bcrypt

from views import blueprint as views_blueprint

app = Flask(__name__)


def setup_app(app):
    app.config.from_object('config')
    app.register_blueprint(views_blueprint)

def setup_db(app):
    db.init_app(app)

def setup_lm(app):
    lm.init_app(app)
    lm.login_view = 'views.login'

def setup_bcrypt(app):
    bcrypt.init_app(app)

def setup(app):
    setup_app(app)
    setup_db(app)
    setup_lm(app)
    setup_bcrypt(app)


def run(app):
    app.run(host=C.HOSTNAME, port=C.PORT, debug=C.DEBUG, threaded=True)
