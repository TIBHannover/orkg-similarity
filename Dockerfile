FROM python:3
LABEL maintainer="Yaser Jaradeh <Yaser.Jaradeh@tib.eu>"

RUN apt-get install -y libpq-dev

WORKDIR /app

# Install application
ADD . /app

# Install requirements
RUN pip install -r requirements.txt

EXPOSE 5000

# Apply the migration to the database and run the application

CMD flask db upgrade && python app.py


