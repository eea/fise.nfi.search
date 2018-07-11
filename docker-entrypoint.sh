#!/bin/sh

set -e

if [ -z "$POSTGRES_HOST" ]; then
    POSTGRES_HOST="postgres"
fi

while ! nc -z ${POSTGRES_HOST} 5432; do
  echo "Waiting for PostgreSQL server at '$POSTGRES_HOST' to accept connections on port 5432..."
  sleep 1s
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
            exec python manage.py runserver 0.0.0.0:${DJANGO_PORT:-8000}
        else
            uwsgi --ini uwsgi.ini
        fi
        ;;
    *)
esac
