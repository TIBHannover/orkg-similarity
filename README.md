# ORKG Similarity and Comparison

To run the Similarity and Comparison framework it needs other services in order to start properly.
Services are managed via [Docker (CE)](https://www.docker.com/community-edition) and [Docker Compose](https://docs.docker.com/compose/)

Note: the code it self needs Python >= 3.6 (Handled by the docker setup)

## Installation

- Create your `.env` file, see `.env.example` for reference.

Install using pip:

    pip install -r requirements.txt

- Run `flask db upgrade` for the first time or to migrate any outstanding model migrations.

## Running

Run the following command using python 3.6:

    python <filename>

### Docker

To run the application as a docker instance:

    docker-compose up -d

This container works **within** the network of the Neo4J instance used with the [Backend](https://gitlab.com/TIBHannover/orkg/orkg-backend). It wont work if it is ran without the required network running.

The docker compose accesses the external network of the backend under the name: `orkg-backend_backend` you can check if this is the name of the network created by the backend docker using the command `docker network ls`, the name of the backend network should match the name in the docker-compose file.

## Notes

* The code assumes the Neo4J installation is running on the default ports and that Neo4J has APOC installed.
* The comparison functionality uses FastText word embeddings to compute similarities. Pretrained binary models of [FastText](https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz) (4.5GB) should be downloaded and placed in a `data` folder.
* The docker image does not contain the model data. Bind mount a volume to `/app/data` to make them available.

### Environment Variables

The code utilises environment variables to init some configurations. Variables used are:

* `SIMCOMP_NEO4J_HOST` used to specify host for Neo4J (default: `localhost`)
* `SIMCOMP_NEO4J_USER` used to specify user to authenticate for Neo4J (default: `neo4j`)
* `SIMCOMP_NEO4J_PASSWORD` used to specify password to authenticate for Neo4J (default: `password`)
* `SIMCOMP_ELASTIC_HOST` used to specify ElasticSearch host and port (default: `localhost:9200`)
* `SIMCOMP_ELASTIC_INDEX` used to specify the index name for ElasticSearch (default: `test`)
* `SIMCOMP_FLASK_HOST` used to specify the host for the flask application (default: `0.0.0.0`)
* `SIMCOMP_FLASK_PORT` used to specify the port for the flask application (default: `5000`)
* `FLASK_DEBUG` used to specify to run the flask application in debug mode (if the variable is set to any value then the application will run in debug)
