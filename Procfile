web: python manage.py migrate && python manage.py reset_admin_password && python manage.py collectstatic --noinput && gunicorn core.wsgi:application
