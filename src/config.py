import os

HOSTNAME = '0.0.0.0'
PORT = 5000
DEBUG = True

BASEDIR = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'db/app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db/db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True

SECRET_KEY = '\xc8`\xb8\x07\x90ok"E\xad\x04\xccV4\x87\xe9\xbb\xec\x12\xf9L\x8d"\x0e'
