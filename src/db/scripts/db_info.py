#!/usr/bin/env python
import os.path
from os import sys

sys.path.append(os.path.dirname(__file__) + "/../../app")
sys.path.append(os.path.dirname(__file__) + "/../../")
from migrate.versioning import api
import config as C

if __name__ == "__main__":
    version = api.db_version(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)
    db_uri = C.SQLALCHEMY_DATABASE_URI
    migrate_uri = C.SQLALCHEMY_MIGRATE_REPO

    print("=== Database Information ===")
    print('Database: ' + db_uri)
    print('Migration Scripts Location: ' + migrate_uri)
    print('Current Version: ' + str(version))