FROM python:3
LABEL maintainer="Yaser Jaradeh <Yaser.Jaradeh@tib.eu>"

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

ADD https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz ./data/cc.en.300.bin.gz

RUN chmod +x ./data/cc.en.300.bin.gz
RUN gunzip ./data/cc.en.300.bin.gz

EXPOSE 5000

CMD [ "python", "api.py" ]

