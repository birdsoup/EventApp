from flask import render_template, flash, redirect, url_for, request, g, Blueprint
from forms import SearchForm

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

    parameters = {'q':search_terms, 'location.address': '700 Commonwealth Ave, Boston MA, 02215', 'location.within': '20mi' }
    response = requests.get(
                        "https://www.eventbriteapi.com/v3/events/search/",
                        headers = {
                            "Authorization": "Bearer " + TOKEN,
                        },
                        verify = True,  # Verify SSL certificate
                        params=parameters)

    result = json.loads(response.text)
    events = result['events']
    return render_template("search_events.html", title="Event Results", events=events)
