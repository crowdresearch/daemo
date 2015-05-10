# Crowdsource Platform - Crowdresearch HCI Stanford

This is a Django 1.8 app using a Postgres database that can be deployed to Heroku.

### Setup

Install [Postgres](http://postgresapp.com/) and create a new database:

    bash> psql
    psql> CREATE DATABASE crowdsource_dev ENCODING 'UTF8';

Create a `local_settings.py` file in the CSP folder and configure it to connect to the Postgres database:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "crowdsource_dev"
        }
    }
Source the virtual environment, install dependencies, and migrate the database:

    bash> source venv/bin/activate
    bash> pip install -r requirements.txt
    bash> python manage.py syncdb
    bash> python manage.py migrate

    bash>brew install node  #use other ways if you don't have brew
    bash>npm install -g bower
    bash>python manage.py bower_install
    bash>cd staticfiles
    bash>bower install ng-grid
    bash>bower install angular-smart-table
    
If you encounter an error `angular-route.js 404`, do this:

    bash> bower cache clean
    bash> rm -fr staticfiles/bower_components
    bash> python manage.py bower_install
    
You will probably be asked which Angular version should be used, choose `1.3.14`.
If there are no errors, you are ready to run the app from your local server:

    bash> python manage.py runserver
    
Where can I get data: 
1) Current file: following data supports tasksearch, task,ranking  
    
    bash> python manage.py loaddata fixtures/neilTaskRankingData.json

OPTIONAL
2) Ranking Dataset  (>800 records already included in #1)

    bash> python manage.py loaddata fixtures/neilCrowdsourcingRankingData.json
 
3) Optional to dump data from environment to the file
   bash> python manage.py dumpdata crowdsourcing > fixtures/neilCrowdsourcingRankingData.json
    
4) How to generate data dynamically with autofixture 

    bash> python manage.py loadtestdata AppName.Model:NUMBER OF RECORDS  
    Example: bash> python manage.py loadtestdata crowdsourcing.UserCounry:15     
   
User Interface:  
![Alt text](http://crowdresearch.stanford.edu/w/img_auth.php/9/9d/NeilGLanding.png "Landing")
![Alt text](http://crowdresearch.stanford.edu/w/img_auth.php/0/0f/NeilReg.png "Registration") 

