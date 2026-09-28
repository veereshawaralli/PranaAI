#!/usr/bin/env bash
# Build script for deploying Prana AI (Django) to Render or similar PaaS.
# Referenced by render.yaml as: bash build.sh
set -o errexit  # abort the build on the first error

pip install --upgrade pip
pip install -r requirements.txt

# Collect static assets for WhiteNoise to serve.
python manage.py collectstatic --no-input

# Apply database migrations.
python manage.py migrate --no-input
