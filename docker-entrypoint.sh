#!/bin/bash

set -e

if [ -z "$POSTGRES_ADDR" ]; then
    POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for PostgreSQL server at '$POSTGRES_ADDR' to accept connections..."
  sleep 3s
done

if [ -z "$TIMEOUT" ]; then
    TIMEOUT=30
fi

if [ "x$DJANGO_MIGRATE" = 'xyes' ]; then
    python manage.py migrate --noinput
fi

if [ "x$DJANGO_COLLECT_STATIC" = "xyes" ]; then
  python manage.py collectstatic --noinput
fi

case "$1" in
    manage)
        exec python manage.py "$1"
        ;;
    run)
        if [ "x$DEBUG" = 'xyes' ]; then
            exec python manage.py runserver 0.0.0.0:${GUNICORN_PORT:-8000}
        else
            exec gunicorn -e SCRIPT_NAME=$SCRIPT_NAME \
                        nfi_search.wsgi:application \
                        --name search \
                        --bind 0.0.0.0:${GUNICORN_PORT:-8000} \
                        --workers 3 \
                        --timeout $TIMEOUT \
                        --access-logfile - \
                        --error-logfile -
            ;;
    *)
esac
