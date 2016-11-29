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

    parameters = {'q':search_terms, 'location.address': form.location.data, 'location.within': '20mi' }
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
            venue_id = event['venue_id']

            print venue_id
            response = requests.get(
                                "https://www.eventbriteapi.com/v3/venues/" + venue_id,
                                headers = {
                                    "Authorization": "Bearer " + TOKEN,
                                },
                                verify = True,
                                params=parameters
                                )
            event['address'] = json.loads(response.text)['address']
            #should probably include a dropdown box or something here to keep reading more

    return render_template("search_events.html", title="Event Results", events=events)

@blueprint.route("/how", methods=['GET'])
def how():
    return render_template("how.html", title="How it all works")

@blueprint.route("/features", methods=['GET'])
def features():
    return render_template("features.html", title="Features")

@blueprint.route("/about", methods=['GET'])
def about():
    return render_template("about.html", title="About")

@blueprint.route("/bookmark/<id>", methods=['GET'])
def bookmark(id):
    return "bookmark " + id + "<br>not implemented yet<br>should probably do this api call in javascript"