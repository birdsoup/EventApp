## To start the web app locally
    ./run.py

## To develop the web app
Install virtualenv and start the dev environment:

    pip install virtualenv
    source dev.sh

## Note:
To make the geolocation work locally you need to visit localhost:5000/ instead of 0.0.0.0:5000 (or on a live server you must support TLS)
Also, the Google Maps API won't work locally, as the key is restricted to the domain name for the site (when it was being hosted).
