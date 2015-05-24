# Crowdsource Platform - Crowdresearch HCI Stanford

[![Build Status](https://travis-ci.org/crowdresearch/crowdsource-platform.svg)](https://travis-ci.org/crowdresearch/crowdsource-platform)


This is a Django 1.8 app using a Postgres database that can be deployed to Heroku.

### Setup

If you are on Windows or encounter issues with these instructions, please try the instructions in the [Setup with Vagrant](#setup-with-vagrant) section.

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
    bash> python manage.py makemigrations oauth2_provider
    bash> python manage.py migrate
    bash> python manage.py makemigrations
    bash> python manage.py migrate

    #users who do not have migrations please run the following commands
    bash> python manage.py makemigrations crowdsourcing
    bash> python manage.py migrate --fake-initial

    bash>brew install node  #use other ways if you don't have brew
    bash>npm install -g bower
    bash>bower install
    bash>cd staticfiles


If you encounter an error `angular-route.js 404`, do this:

    bash> bower cache clean
    bash> rm -fr staticfiles/bower_components
    bash> bower install
    
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
    Example: bash> python manage.py loadtestdata crowdsourcing.UserCountry:15
   
User Interface:  
![Alt text](http://crowdresearch.stanford.edu/w/img_auth.php/9/9d/NeilGLanding.png "Landing")
![Alt text](http://crowdresearch.stanford.edu/w/img_auth.php/0/0f/NeilReg.png "Registration") 

### Setup with Vagrant

This approach might be useful if you're on Windows or have trouble setting up postgres, python, nodejs, git, etc. It will run the server in a virtual machine.

First install [Virtualbox](https://www.virtualbox.org/) [Vagrant](https://www.vagrantup.com/) and [Git](http://git-scm.com/downloads)

Clone this repo to get the code:

    git clone https://github.com/crowdresearch/crowdsource-platform.git
    cd crowdsource-platform

Then run the command:

    vagrant up

This will set up an Ubuntu VM, install prerequisites, create databases, and start the machine. Then run:

    vagrant ssh

This will now give you a shell in your virtual machine.  It will automatically cd to /home/vagrant/crowdsource-platform where the code is (this is a shared folder with the host machine)

Now you can run the server:

    python manage.py runserver [::]:8000

And you can visit the website by going to http://localhost:8000 in your web browser.

On subsequent runs, you only need to run:

    vagrant up
    vagrant ssh
    python manage.py runserver [::]:8000
