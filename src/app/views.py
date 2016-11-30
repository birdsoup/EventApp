from flask import render_template, flash, redirect, url_for, request, g, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from login_manager import lm
from database import db, validate_credentials, User


from forms import SearchForm, LoginForm, SignupForm
from hasher import hash_password


import requests
import json

TOKEN = 'W4B3Z3RYXUKWIUCB2RER'

blueprint = Blueprint("views", "views")

@blueprint.route('/')
@blueprint.route('/index')
def index():
    return render_template("index.html", title='Home', search_form=SearchForm())


@blueprint.route('/search_events', methods=['POST'])
def search_events():
    #add api call here
    form = SearchForm(request.form)
    search_terms = form.search_terms.data

    parameters = {'q':search_terms, 'location.address': form.location.data, 'location.within': '20mi', 'expand':'venue' }
    response = requests.get(
                        "https://www.eventbriteapi.com/v3/events/search/",
                        headers = {
                            "Authorization": "Bearer " + TOKEN,
                        },
                        verify = True,
                        params=parameters)

    result = json.loads(response.text)
    events = result['events']

    for event in events:
        description = event['description']['text']
        if description is not None and len(description) > 1000:
            event['description']['text'] = event['description']['text'][:1000] + "..."

            #should probably include a dropdown box or something here to keep reading more

    return render_template("search_events.html", title="Event Results", events=events)

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
            print(form.errors)

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
            flash("something's wrong")

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
@blueprint.route("/bookmark/<id>", methods=['GET'])
def bookmark(id):
    return "bookmark " + id + "<br>not implemented yet<br>should probably do this api call in javascript"


#this function was copied from StackOverflow
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s Error: %s" % (getattr(form, field).label.text, error))