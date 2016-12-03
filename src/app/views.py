from flask import render_template, flash, redirect, url_for, request, g, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from login_manager import lm
from database import db, validate_credentials, User, BookmarkCounter, UserBookmark, EVENTBRITE, STUBHUB, YELP

from forms import SearchForm, LoginForm, SignupForm
from hasher import hash_password
from config import EVENTBRITE_TOKEN

import requests
import json
from datetime import datetime, timedelta
import calendar


blueprint = Blueprint("views", "views")



@blueprint.route('/')
@blueprint.route('/index')
def index():
    ip = request.environ['REMOTE_ADDR']
    try:
        response = requests.get("http://ip-api.com/json/" + ip, timeout=5)
    except requests.exceptions.Timeout:
        address = "Error while finding location"
        return render_template("index.html", title='Home', search_form=SearchForm(), location=address)

    location = json.loads(response.text)
    if location['status'] == 'success':
        address= location['city'] + ', ' + location['region']
    else:
        address = "Location not found"

        #DEBUGGING REMOVE ON REAL SERVER
        address = "Boston, MA"

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
    try:
        response = requests.get(
                            "https://www.eventbriteapi.com/v3/events/search/",
                            headers = {"Authorization": "Bearer " + EVENTBRITE_TOKEN},
                            verify = True,
                            params=parameters, 
                            timeout=5)
    except requests.exceptions.Timeout:
        flash("Error while contacting events API")
        return redirect(url_for('.index'))

    result = json.loads(response.text)

    if 'status_code' in result and result['status_code'] == 400:
        if result['error_description'] == "There are errors with your arguments: location.address - INVALID":
            flash('Error - Invalid location')
        else:
            flash('Error - Something was wrong with your search')
        return redirect(url_for('.index'))
    if 'events' in result:
        events = result['events']
    else:
        flash('Error - Something went wrong.')
        return redirect(url_for('.index'))

    #truncate the description if it's too long
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


#this is vulnerable to csrf, might want to switch to using forms
#should call this from the front-end in javascript instead of linking to it.
@login_required
@blueprint.route("/bookmark/<bookmark_id>/<source>", methods=['GET'])
def bookmark(bookmark_id, source):
    '''Bookmarks the event with the given id from the given source (Eventbrite, stubhub or yelp)'''
    if g.user is not None and g.user.is_authenticated:
        #used to determine whether to incremend or decrement bookmark count
        adding_bookmark = True

        user_bookmark = UserBookmark.query.filter_by(bookmark_id=bookmark_id, source=source, user=g.user)
        #if not bookmarked, add it, else delete it
        if user_bookmark.scalar() is None:
            user_bookmark = UserBookmark(bookmark_id=bookmark_id, source=source, user=g.user)
            db.session.add(user_bookmark)
            flash("Bookmark added.")
        else:
            adding_bookmark = False
            db.session.delete(user_bookmark.first())
            flash("Bookmark removed.")


        counter = BookmarkCounter.query.filter_by(bookmark_id=bookmark_id, source=source)
        if counter.scalar() is None:
            counter = BookmarkCounter(bookmark_id=bookmark_id, source=source, count=1)
            db.session.add(counter)
            #should probably move this to the frontend, do the call to it from javascript instead of 
            #changing pages
            #return redirect(url_for('.index'))
        else:
            if adding_bookmark:
                counter.first().count += 1
            else:
                count = counter.first().count
                if count == 1:
                    db.session.delete(counter.first())
                else:
                    counter.first().count -= 1





        db.session.commit()

    if "view_event" in request.referrer:
        return redirect(request.referrer)

    return redirect(request.args.get('next') or url_for('.index'))



@login_required
@blueprint.route("/bookmarks", methods=['GET'])
def bookmarks():
    user_bookmarks = UserBookmark.query.filter_by(user=g.user)
    if user_bookmarks is None:
        return render_template("bookmarks.html", title="Your Bookmarks", bookmarks=[])

    user_bookmarks = user_bookmarks.all()
    bookmark_ids = [bookmark.bookmark_id for bookmark in user_bookmarks]

    events = batch_event_request(bookmark_ids)
    if events == -1:
        flash("Error while contacting event API")
        return render_template("bookmarks.html", title="Your Bookmarks", events=[], source=EVENTBRITE)

    return render_template("bookmarks.html", title="Your Bookmarks", events=events, source=EVENTBRITE)

@blueprint.route("/help", methods=['GET'])
def help():
    return render_template("help.html", title="Help")

@blueprint.route("/popular_events", methods=['GET'])
def popular_events():
    popularEvents = BookmarkCounter.query.order_by(BookmarkCounter.count.desc()).all()[:10]
    events = batch_event_request([event.bookmark_id for event in popularEvents])

    return render_template("popular_events.html", title="Popular Events", events=events, counters=popularEvents, source=EVENTBRITE)


@blueprint.route("/view_event/<event_id>", methods=['GET'])
def view_event(event_id):
    try:
        response = requests.get(
                            "https://www.eventbriteapi.com/v3/events/" + str(event_id) + "?expand=venue,ticket_classes",
                            headers = {"Authorization": "Bearer " + EVENTBRITE_TOKEN},
                            verify = True,
                            timeout=5)

    except requests.exceptions.Timeout:
        flash("Error while contacting events API")
        return redirect(url_for('.index'))

    result = json.loads(response.text)

    if 'description' not in result:
        flash("Error - There was an issue getting the event info")
        return redirect(url_for('.index'))

    #default values
    weather_img = None
    weather_str = "Weather info could not be found."

    start_date = result['start']['local'][:10] # xxxx-xx-xx date representation
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if True: #start_date < datetime.now() + timedelta(days=4):

        try:
            time = calendar.timegm(start_date.utctimetuple())
            DARKSKY_KEY = 'da09fc59cbac70c0350780fe1cda2b91'
            response = requests.get(
                                "https://api.darksky.net/forecast/%s/%s,%s,%s" % (DARKSKY_KEY, result['venue']['latitude'], result['venue']['longitude'], str(time)),
                                verify = True,
                                timeout=5)

            weather_dict = json.loads(response.text)['daily']['data'][0]
            temperatureMin = weather_dict['temperatureMin']
            temperatureMax = weather_dict['temperatureMax'] 
            humidity = weather_dict['humidity']
            summary = weather_dict['summary']
            #days_weather = json.dumps(weather_dict, indent=4, sort_keys=True) 
            weather_str = "%i - %i degrees, %s%% humidity, %s" % (temperatureMin, temperatureMax, str(humidity)[2:], summary)
            print weather_str

        except requests.exceptions.Timeout:
            return redirect(url_for('.index'))
    else:
        weather_str = "Event date is too far away for a weather forecast."





    return render_template('view_event.html', title="Event Info", event=result, source=EVENTBRITE, weather=weather_str, location=result['venue']['address']['localized_address_display'])




#this function was copied from http://flask.pocoo.org/snippets/12/
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))


def batch_event_request(event_ids):
    '''

    '''
    params = []
    for event_id in event_ids:
        params.append({"method": "GET", "relative_url": "/events/" + str(event_id) + "?expand=venue"})

    params = json.dumps(params)

    parameters = {'batch':params}
    try:
        response = requests.post(
                            "https://www.eventbriteapi.com/v3/batch/",
                            headers = {"Authorization": "Bearer " + EVENTBRITE_TOKEN},
                            verify = True,
                            params=parameters,
                            timeout=5)
    except requests.exceptions.Timeout:
        return -1

    event_dict = json.loads(response.text)
    events = []
    for event in event_dict:
        events.append(json.loads(event['body']))

    return events


#For use in the jinja templates, to determine how to label the bookmark buttons
@blueprint.context_processor
def processor():
    def is_bookmarked(bookmark_id):
        if g.user is not None and g.user.is_authenticated:
            try:
                if UserBookmark.query.filter_by(bookmark_id=bookmark_id, user=g.user).scalar() is not None:
                    return True
            except:
                return False

        return False
    return dict(is_bookmarked=is_bookmarked)
