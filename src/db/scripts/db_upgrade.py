#!/usr/bin/env python

import os.path
from os import sys
sys.path.append(os.path.dirname(__file__) + "/../../app")
sys.path.append(os.path.dirname(__file__) + "/../../")
from migrate.versioning import api
import config as C


if __name__ == '__main__':
    api.upgrade(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(C.SQLALCHEMY_DATABASE_URI, C.SQLALCHEMY_MIGRATE_REPO)

    print('Current database version: ' + str(v))

