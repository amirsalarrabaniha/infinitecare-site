web: cd backend && python manage.py migrate --noinput && python manage.py load_initial_content && python manage.py collectstatic --noinput && gunicorn config.wsgi --bind 0.0.0.0:$PORT
