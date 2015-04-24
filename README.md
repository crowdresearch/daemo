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

    bash>brew install node  #use other ways if you don't have brew
    bash>npm install -g bower
    bash>python manage.py bower_install

If there are no errors, you are ready to run the app from your local server:

    bash> python manage.py runserver
    
![Alt text](http://crowdresearch.stanford.edu/w/img_auth.php/9/9d/NeilGLanding.png "Landing")


