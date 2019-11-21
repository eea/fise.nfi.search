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
        cd fise.nfi.search

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

## Ubuntu elasticsearch container error:
* If your host runs ubuntu your elasticsearch container may fail to run with the error "bootstrap checks failed".
  This happens because max map count is set under the value __262144__
* You can fix this temporarily(till you restart your machine) by running:

        sudo sysctl -w vm.max_map_count=262144
* You can fix this permanently by modifying your max_map_count file:

        sudo vim /proc/sys/vm/max_map_count
  Change the value from the file with 262144 and save


## Importing data

Data import is based on Excel files containing metadata records and paths to associated data files.  

Data files must be placed in the directory specified by the `IMPORT_FILES_DIR` environment variable. 
  
The `load_metadata` management command is used to perform the import , e.g.:

    ./manage.py load_metadata --original-path-root=Z:\\FISEAPPS\\FISEPRO\\New_Content <Excel file path>

This will:
- Create any new metadata cetagories found in the Excel file.
- Import document metadata records as part of a new `DocumentImportBatch`.
- Copy document files referenced by metadata records from the directory indicated by `$IMPORT_FILES_DIR`, 
to the data files directory `$FILES_DIR`.   
 
Note that the path specified by option `original-path-root` must be the common base directory for _all_ data files 
paths in the Excel file (data staging is currently being done on Windows machines, thus the base path above). 

After each new import, run the following command to rebuild the ElasticSearch index:
      
    ./manage.py search_index --rebuild --parallel
