# Crowdsource Platform - Crowdresearch HCI Stanford

This is a Django 1.8 app using a Postgres database that can be deployed to Heroku.

### Setup

Install [Postgres](http://postgresapp.com/) and create a new database:

    bash> psql
    psql> CREATE DATABASE crowdsource_dev ENCODING 'UTF8';

Create a `local_settings.py` file and configure it to connect to the Postgres database:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "crowdsource_dev"
        }
    }

Source the virtual environment, install dependencies, and migrate the database:

    bash> source venv/bin/activate
    bash> pip install -r requirements.txt
    bash> python manage.py migrate

    currently we have an issue with User model from Django as it's cannot be used in an app with no migrations, please follow these steps
    1. comment out the crowdsourcing app in the crowdresearch.settings file INSTALLED_APPS
    2. run python3.4 manage.py syncdb
    3. uncomment the commented app from step 1
    4. run python3.4 manage.py syncdb
    5. if prompted to create a new user, please don't do so, use the web frontend to create a user, this will create a profile as well

If there are no errors, you are ready to run the app from your local server:

    bash> python manage.py runserver

