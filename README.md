# ORKG Similarity and Comparison

## Installation

Install using pip:

    pip install -r requirements.txt


## Running 
Run the following command (for now) using python 3.6:

    python <filename>
    

## Notes
* The code assumes the Neo4J installation is running on the default ports and that Neo4J has APOC installed.
* The comparison functionality uses FastText word embeddings to compute similarities. Pretrained binary models of [FastText](https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz) (4.5GB) should be downloaded and placed in a `data` folder