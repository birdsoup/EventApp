#!/usr/bin/env python
import os.path
from os import sys
from migrate.versioning import api

sys.path.append(os.path.dirname(__file__) + "/../../app")
sys.path.append(os.path.dirname(__file__) + "/../../")


from app import app, setup_app
from database import db
import config as C

if __name__ == '__main__':
    setup_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    if not os.path.exists(C.SQLALCHEMY_MIGRATE_REPO):
        api.create(C.SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO, api.version(C.SQLALCHEMY_MIGRATE_REPO))

    print("Database created")