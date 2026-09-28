web: gunicorn medibuddy_project.wsgi:application --bind 0.0.0.0:${PORT:-8000}
release: python manage.py migrate --no-input
