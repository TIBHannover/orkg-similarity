FROM python:3.6
LABEL maintainer="Yaser Jaradeh <Yaser.Jaradeh@tib.eu>"

WORKDIR /app

RUN apt-get install -y libpq-dev

ADD requirements.txt /app

# Install requirements
RUN \
  pip install --upgrade pip && \
  pip install --no-cache -r requirements.txt && \
  rm -rf ~/.cache/

# Install application
ADD . /app

EXPOSE 5000

# Apply the migration to the database and run the application
CMD flask db upgrade && python app.py
