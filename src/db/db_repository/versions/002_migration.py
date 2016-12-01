from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
bookmark_counter = Table('bookmark_counter', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('bookmark_id', Integer),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('source', Integer),
)

user_bookmark = Table('user_bookmark', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('bookmark_id', Integer),
    Column('source', Integer),
    Column('user_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['bookmark_counter'].create()
    post_meta.tables['user_bookmark'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['bookmark_counter'].drop()
    post_meta.tables['user_bookmark'].drop()
