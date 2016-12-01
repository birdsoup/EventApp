from flask import render_template, flash, redirect, url_for, request, g, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from login_manager import lm
from database import db, validate_credentials, User, BookmarkCounter, UserBookmark, EVENTBRITE, STUBHUB, YELP

from forms import SearchForm, LoginForm, SignupForm
from hasher import hash_password
from config import EVENTBRITE_TOKEN

import requests
import json


blueprint = Blueprint("views", "views")



@blueprint.route('/')
@blueprint.route('/index')
def index():
    ip = request.environ['REMOTE_ADDR']
    response = requests.get(
                        "http://ip-api.com/json",
                        params={'ip':ip}
                        )
    location = json.loads(response.text)
    if location['status'] == 'success':
        address= location['city'] + ', ' + location['region']
    else:
        address = "Location not found"
    return render_template("index.html", title='Home', search_form=SearchForm(), location=address)



@blueprint.route('/search_events', methods=['POST'])
def search_events():
    #add api call here
    form = SearchForm(request.form)
    if not form.validate():
        flash_errors(form)
        return redirect(url_for('.index'))


    search_terms = form.search_terms.data

    distance = form.distance.data
    possible_distances = ["2km", "5km", "10km", "20km"]
    if distance not in possible_distances:
        distance = ""

    if form.category.data is not None:
        search_terms += " " + form.category.data

    parameters = {'q':search_terms, 'location.address': form.location.data, 'location.within': distance, 'expand':'venue' }
    response = requests.get(
                        "https://www.eventbriteapi.com/v3/events/search/",
                        headers = {
                            "Authorization": "Bearer " + EVENTBRITE_TOKEN,
                        },
                        verify = True,
                        params=parameters)

    result = json.loads(response.text)
    #print result
    if 'status_code' in result and result['status_code'] == 400:
        flash('Error - Something was wrong with your search')
        return redirect(url_for('.index'))
    if 'events' in result:
        events = result['events']
    else:
        flash('Error - Something went wrong.')
        return redirect(url_for('.index'))

    for event in events:
        description = event['description']['text']
        if description is not None and len(description) > 1000:
            event['description']['text'] = event['description']['text'][:1000] + "..."

            #should probably include a dropdown box or something here to keep reading more

    return render_template("search_events.html", title="Event Results", events=events, source=EVENTBRITE)




@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # User is logged in already, send them back to the index        
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('.index'))

    if request.method == 'GET':
        return render_template("register.html", title="Sign Up", signup_form=SignupForm())

    form = SignupForm(request.form)

    if request.method == 'POST':
        if form.validate():
            if User.query.filter_by(username=form.username.data).scalar() is None:
                if User.query.filter_by(email=form.email.data).scalar() is None:
                    user = User(username=form.username.data, email=form.email.data,
                                passwordhash=hash_password(form.password.data))
                    db.session.add(user)
                    db.session.commit()
                    flash('Thanks for registering!')
                    login_user(user, remember=False)
                    return redirect(url_for('.index'))
                else:
                    flash('Error: Email is already in use')
            else:
                flash('Error: Username is already in use')
        else:
            flash_errors(form)

    return redirect(url_for('.register'))




@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('.index'))

    if request.method == 'GET':
        return render_template("login.html", title="Log In", login_form=LoginForm())

    form = LoginForm(request.form)

    if request.method == 'POST':
        if form.validate():
            if validate_credentials(form.username.data, form.password.data):
                flash('Login Successful')

                user = User.query.filter_by(username=form.username.data).one()
                login_user(user, remember=form.remember_me)
                return redirect(url_for('.index'))

            else:
                flash('Error: Incorrect login')

        else:
            flash_errors(form)

    return redirect(url_for('.login'))



@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.index'))



@lm.user_loader
def load_user(id):
    return User.query.get(int(id))



@blueprint.before_request
def before_request():
    g.user = current_user



@blueprint.route("/how", methods=['GET'])
def how():
    return render_template("how.html", title="How it all works")



@blueprint.route("/features", methods=['GET'])
def features():
    return render_template("features.html", title="Features")



@blueprint.route("/about", methods=['GET'])
def about():
    return render_template("about.html", title="About")



#this is vulnerable to csrf, might want to switch to using forms
#should call this from the front-end in javascript instead of linking to it.
@login_required
@blueprint.route("/bookmark/<bookmark_id>/<source>", methods=['GET'])
def bookmark(bookmark_id, source):
    '''Bookmarks the event with the given id from the given source (Eventbrite, stubhub or yelp)'''
    if g.user is not None and g.user.is_authenticated:
        counter = BookmarkCounter.query.filter_by(bookmark_id=bookmark_id, source=source)
        if counter.scalar() is None:
            counter = BookmarkCounter(bookmark_id=bookmark_id, source=source, count=0)
            db.session.add(counter)
            #should probably move this to the frontend, do the call to it from javascript instead of 
            #changing pages
            #return redirect(url_for('.index'))
        else:
            counter.first().count += 1

        user_bookmark = UserBookmark.query.filter_by(bookmark_id=bookmark_id, source=source, user=g.user)
        #if not bookmarked, add it, else delete it
        if user_bookmark.scalar() is None:
            user_bookmark = UserBookmark(bookmark_id=bookmark_id, source=source, user=g.user)
            db.session.add(user_bookmark)
            flash("Bookmark added.")
        else:
            db.session.delete(user_bookmark.first())
            flash("Bookmark removed.")


        db.session.commit()

    return redirect(request.args.get('next') or url_for('.index'), code=307)



@login_required
@blueprint.route("/bookmarks", methods=['GET'])
def bookmarks():
    user_bookmarks = UserBookmark.query.filter_by(user=g.user)
    if user_bookmarks is None:
        return render_template("bookmarks.html", title="Your Bookmarks", bookmarks=[])

    user_bookmarks = user_bookmarks.all()
    params = []
    for bookmark in user_bookmarks:
        params.append({"method": "GET", "relative_url": "/events/" + str(bookmark.bookmark_id), "body":"expand=venue"})

    params = json.dumps(params)

    parameters = {'batch':params, 'expand':'venue'}
    response = requests.post(
                        "https://www.eventbriteapi.com/v3/batch/",
                        headers = {
                            "Authorization": "Bearer " + EVENTBRITE_TOKEN,
                        },
                        verify = True,
                        params=parameters)
    event_dict = json.loads(response.text)
    events = []
    for event in event_dict:
        events.append(json.loads(event['body']))

    return render_template("bookmarks.html", title="Your Bookmarks", events=events, source=EVENTBRITE)

@blueprint.route("/help", methods=['GET'])
def help():
    render_template("help.html", title="Help")


#this function was copied from StackOverflow
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s Error: %s" % (getattr(form, field).label.text, error))



#def is_bookmarked(bookmark_id, source):
