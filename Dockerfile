FROM python:3.6-slim

ARG REQUIREMENTS_FILE=requirements.dep.txt

ENV APP_HOME=/var/local/fise.nfi.search

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends curl \
    && curl -sL https://deb.nodesource.com/setup_8.x | bash - \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN runDeps="vim netcat libpq-dev nodejs yarn" \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends $runDeps \
    && apt-get clean \
    && rm -vrf /var/lib/apt/lists/*

RUN mkdir -p $APP_HOME

COPY yarn.lock package*.json requirements.txt $REQUIREMENTS_FILE $APP_HOME/
WORKDIR $APP_HOME

RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE

RUN npm_config_tmp=$APP_HOME yarn

COPY . $APP_HOME

RUN npm run build

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
CMD ["run"]
