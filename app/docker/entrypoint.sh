#!/bin/sh
set -eu
python manage.py migrate --noinput
exec gunicorn klasse5e.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -
