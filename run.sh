#!/bin/bash

ls -a
# activate venv
#.venv/bin/activate

# copy static files to directory for http server
.venv/bin/python manage.py collectstatic --noinput

# run DB migrations if necessary
.venv/bin/python manage.py migrate

# start recorder in background and terminate on script exit
.venv/bin/python manage.py recorder &
RECORDER_JOB=$!
trap 'kill $RECORDER_JOB' EXIT HUP TERM INT

# run django app
.venv/bin/gunicorn -w 2 --bind 0.0.0.0:8000 Spybot2.wsgi
