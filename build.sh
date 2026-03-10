#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Run migrations and collect static files
python config/manage.py migrate
python config/manage.py collectstatic --no-input
