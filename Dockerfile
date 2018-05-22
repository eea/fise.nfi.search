FROM python:3.6-slim

ARG REQUIREMENTS_FILE=requirements.dep.txt

ENV PROJ_DIR=/var/local/nfi-search

RUN runDeps="vim netcat libpq-dev" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

RUN mkdir -p $PROJ_DIR
COPY . $PROJ_DIR
WORKDIR $PROJ_DIR


RUN pip install --no-cache-dir -r $REQUIREMENTS_FILE

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]
