# ORKG Similarity and Comparison

To run the Similarity and Comparison framework it needs other services in order to start properly.
Services are managed via [Docker (CE)](https://www.docker.com/community-edition) and [Docker Compose](https://docs.docker.com/compose/)

Note: the code it self needs Python >= 3.6 (Handled by the docker setup)

## Installation

Create your `.env` file, see `.env.example` for reference.

Install using pip:

    pip install -r requirements.txt

Run `flask db upgrade` for the first time or to migrate any outstanding model migrations.

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

### Environment Variables

The code utilises environment variables to init some configurations. Variables used are:

| # Flask                        | *The following variables used to configure the flask application*                                                                  |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| SIMCOMP_FLASK_HOST             | The hostname to listen on. Set this to '0.0.0.0' to have the server available externally as well.                                  |
| SIMCOMP_FLASK_PORT             | The port of the webserver. Defaults to 5000                                                                                        |
| FLASK_APP                      | Used to specify how to load the application for the 'flask' command.                                                               |
| FLASK_ENV                      | 'development' or 'production' and it's used to indicate to Flask, extensions, and other programs what context Flask is running in. |
| FLASK_DEBUG                    | Whether debug mode is enabled. **Do not enable debug mode when deploying in production.**                                          |
| # DB                           | *The following variables used to configure connection to the postgres instance*                                                    |
| POSTGRES_USER                  | Used by docker-compose to set the user of PostgreSQL image                                                                         |
| POSTGRES_PASSWORD              | Used by docker-compose to set the password of PostgreSQL image                                                                     |
| POSTGRES_DB                    | Used by docker-compose to set the database name of PostgreSQL image                                                                |
| SQLALCHEMY_DATABASE_URI        | Used to connect to the database of PostgreSQL image in the flask application                                                       |
| SQLALCHEMY_TRACK_MODIFICATIONS | Set to 'False' to save system resources because the event system of SQL Alchemy is not used in this application.                   |
| # NEO4J                        | *The following variables used to connect to the NEO4J instance*                                                                    |
| SIMCOMP_NEO4J_HOST             | Neo4J server host                                                                                                                  |
| SIMCOMP_NEO4J_USER             | Neo4J user                                                                                                                         |
| SIMCOMP_NEO4J_PASSWORD         | Neo4J password                                                                                                                     |
| # ELASTIC                      | *The following variables used to connect to the Elastic search instance*                                                           |
| SIMCOMP_ELASTIC_HOST           | Elastic search server host                                                                                                         |
| SIMCOMP_ELASTIC_INDEX          | Elastic search index                                                                                                               |
| # HOSTS                        | *Hosts*                                                                                                                              |
| API_HOST                       | Host for the ORKG backend API (e.g. https://orkg.org/api/)                                                                         |
| SIMCOMP_HOST                   | Elastic search index (e.g. https://orkg.org/simcomp/)                                                                             |

