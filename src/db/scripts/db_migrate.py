#!/usr/bin/env python
import imp

import os.path
from os import sys
sys.path.append(os.path.dirname(__file__) + "/../../app")
sys.path.append(os.path.dirname(__file__) + "/../../")
from migrate.versioning import api

import config as C
from database import db

if __name__ == '__main__':
    # Create the db data model
    old_version = api.db_version(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)
    exec(old_model, tmp_module.__dict__)

    # Generate the migration script, and write it
    script = api.make_update_script_for_model(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO, tmp_module.meta,
                                              db.metadata)
    migration = C.SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (old_version+1))
    open(migration, "wt").write(script)

    # Upgrade the db
    api.upgrade(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)

    print('New migration saved as ' + migration)
    print('Current database version: ' + str(v))
