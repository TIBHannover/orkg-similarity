# ORKG Similarity and Comparison

## Installation

Install using pip:

    pip install -r requirements.txt


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
* The comparison functionality uses FastText word embeddings to compute similarities. Pretrained binary models of [FastText](https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz) (4.5GB) should be downloaded and placed in a `data` folder. (This is done by the Dockerfile automatically)
* The docker image downloaded the FastText models directly, so it could take a while to build the image.