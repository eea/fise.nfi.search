# NFI search

[![Travis](https://travis-ci.org/eea/fise.nfi.search.svg?branch=master)](
https://travis-ci.org/eea/fise.nfi.search)
[![Coverage](https://coveralls.io/repos/github/eea/fise.nfi.search/badge.svg?branch=master)](https://coveralls.io/github/eea/fise.nfi.search?branch=master)
[![Docker](https://dockerbuildbadges.quelltext.eu/status.svg?organization=eeacms&repository=fise.nfi.search)](https://hub.docker.com/r/eeacms/fise.nfi.search/builds)

Import, store and search National Forests Information documents coming from different MS countries.

The documents are provided in standardized format like spreadsheets, in different languages. They are indexed by metadata and content in order to be searched and filtered by different pre-established criteria.

### Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

### Installing the application
1. Get the source code:

        git clone git@github.com:eea/fise.nfi.search.git
        cd copernicus-insitu-db

1. Customize env files and `docker-compose.override.yml`:

        cp docker/app.env.example docker/app.env
        vim docker/app.env
        cp docker/postgres.env.example docker/postgres.env
        vim docker/postgres.env
        cp docker-compose.override.yml.example docker-compose.override.yml
        vim docker-compose.yml
        
1. Start application stack:

        docker-compose up -d
        

### Install VUE app

1. Install dependencies:

        yarn add

1. Run project: 
        
        npm run dev

1. Add package: 
        
        yarn add "package name"
