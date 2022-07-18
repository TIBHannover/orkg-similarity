FROM python:3.7
LABEL maintainer="Yaser Jaradeh <Yaser.Jaradeh@tib.eu>"

WORKDIR /app

ADD requirements.txt /app

# Install requirements
RUN \
  pip install --upgrade pip && \
  pip install --no-cache -r requirements.txt && \
  rm -rf ~/.cache/

# Add the rest of the code to the app folder
ADD . /app

EXPOSE 5000

# Apply the migration to the database and run the application
CMD flask db upgrade && python app.py
