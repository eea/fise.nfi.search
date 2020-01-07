FROM python:3.6-slim

ARG SCRIPT_NAME

# Overriden in compose as needed
ENV SCRIPT_NAME=$SCRIPT_NAME

ARG REQUIREMENTS_FILE=requirements.txt
ENV APP_HOME=/var/local/fise.nfi.search
RUN runDeps="apt-utils netcat libpq-dev" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $runDeps \
    && apt-get clean \
    && rm -vrf /var/lib/apt/lists/*
RUN mkdir -p $APP_HOME
COPY $REQUIREMENTS_FILE $APP_HOME/
WORKDIR $APP_HOME
RUN buildDeps="build-essential gcc" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $buildDeps \
    && pip install --no-cache-dir -r $REQUIREMENTS_FILE \
    && apt-get -y remove --purge --auto-remove $buildDeps
COPY . $APP_HOME

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["run"]
