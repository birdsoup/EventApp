from flask_sqlalchemy import SQLAlchemy

from hasher import validate

db = SQLAlchemy()

EVENTBRITE = 1
STUBHUB = 2
YELP = 3

def validate_credentials(user, password):
    """Validate credentials
    """
    try:
        passwordhash = User.query.filter_by(username=user).one().passwordhash
    except:
        return False

    return validate(passwordhash, password)


class User(db.Model):
    '''DB model to store users' infromation'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    passwordhash = db.Column(db.String(120), index=True, unique=True)
    bookmarks = db.relationship('UserBookmark', backref='user', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id) 

    def __repr__(self):
        return '<User %r>' % (self.username)

class UserBookmark(db.Model):
    '''DB model to store a bookmark for a particular user'''
    id = db.Column(db.Integer, primary_key=True)
    bookmark_id = db.Column(db.Integer)
    source = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class BookmarkCounter(db.Model):
    '''DB model to count how many bookmarks there are for certain events'''
    id = db.Column(db.Integer, primary_key=True)
    bookmark_id = db.Column(db.Integer)
    count = db.Column(db.Integer, default=0)
    source = db.Column(db.Integer)
