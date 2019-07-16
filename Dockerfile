FROM python:3
LABEL maintainer="Yaser Jaradeh <Yaser.Jaradeh@tib.eu>"

RUN apt-get install -y libpq-dev

# Install FastText binary models
RUN \
  mkdir -p /app/data && \
  cd /app/data && \
  wget --no-verbose https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz && \
  gunzip cc.en.300.bin.gz

WORKDIR /app

# Install application
ADD . /app

# Install requirements
RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "api.py" ]

