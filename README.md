# Crowdsource Platform - Crowdresearch HCI Stanford

[![Build Status](https://travis-ci.org/crowdresearch/crowdsource-platform.svg)](https://travis-ci.org/crowdresearch/crowdsource-platform)


This is a Django 1.8 app using a Postgres database that can be deployed to Heroku.

### Setup

[Please follow the GitHub tutorial](http://crowdresearch.stanford.edu/w/index.php?title=BranchingStrategy) to setup the repository.  

If you are on Windows or want a simpler (automatic) setup process, please try the instructions in the [Setup with Vagrant](#setup-with-vagrant) section. Solutions to common errors can found on the [FAQ page](http://crowdresearch.stanford.edu/w/index.php?title=FAQs)

Install [Postgres](http://postgresapp.com/) and create a new database:

    bash> psql
    psql> CREATE DATABASE crowdsource_dev ENCODING 'UTF8';

Create a `local_settings.py` file in the project root folder and configure it to connect to the Postgres database:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "crowdsource_dev"
        }
    }
    
    DEBUG = True
    COMPRESS_OFFLINE = False
    COMPRESS_ENABLED = False

Make sure you have [Python](https://www.python.org/downloads/) installed. Test this by opening a command line terminal and typing `python'. 

Install [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) to manage a local setup of your python packages. Go into the directory with the checkout of the code and create the Python virtual environment:

    bash> virtualenv venv

Source the virtual environment, install dependencies, and migrate the database:

    bash> source venv/bin/activate
    bash> pip install -r requirements.txt
    bash> python manage.py makemigrations oauth2_provider
    bash> python manage.py migrate

If this is your first time setting it up, you need to initialize your migrations and database:

    bash> python manage.py makemigrations
    bash> python manage.py migrate

If you instead have a database but do not have migrations:

    bash> python manage.py makemigrations crowdsourcing
    bash> python manage.py migrate --fake-initial
    
Install node.js. If you have a Mac, we recommend using [Homebrew](http://brew.sh/). Then:

    bash> brew install node
    
For Ubuntu or Debian:

    bash> sudo apt-get update
    bash> sudo apt-get install nodejs nodejs-legacy npm
    
Now, you can install the dependencies, which are managed by a utility called Bower:

    bash> npm install -g bower
    bash> bower install


    
If there are no errors, you are ready to run the app from your local server:

    bash> python manage.py runserver
    
To serve the local site over https, a sample certificate and key are provided in the repo. To start it, use this command instead of the ```runserver``` command above:

    gunicorn -b 127.0.0.1:8000 -b [::1]:8000 csp.wsgi --workers 2 --keyfile private_key.pem --certfile cacert.pem

This uses the ```gunicorn``` server, which is used in production as well. Here, ```--workers``` determines the number of instances of the server that will be created. In most cases, 1 will work just fine.

And you can visit the website by going to https://127.0.0.1:8000 in your web browser.

You will see a untrusted certificate message in most modern browsers. For this site (and this site only), you may ignore this warning and proceed to the site.

Where can I get data?
1) Current file: following data supports tasksearch, task, ranking  
    
    bash> python manage.py loaddata fixtures/neilCrowdsourcingRankingData.json
    bash> python manage.py loaddata fixtures/neilTaskProfileData.json
    bash> python manage.py loaddata fixtures/dmorinaCategoryData.json 


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

First install [Virtualbox](https://www.virtualbox.org/) and [Vagrant](https://www.vagrantup.com/).

If you are on Windows, you should also install [Git](http://msysgit.github.io/). During the setup process, select "Use Git and optional Unix tools from the Windows Command Prompt" (on the "Adjusting your PATH environment" page), and "Checkout as-is, commit Unix-style line endings" (on the "Configuring the line ending conversions" page).

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

To serve the local site over https, a sample certificate and key are provided in the repo. To start it, use this command instead of the ```runserver``` command above:

    gunicorn -b 127.0.0.1:8000 -b [::1]:8000 csp.wsgi --workers 2 --keyfile private_key.pem --certfile cacert.pem

This uses the ```gunicorn``` server, which is used in production as well. Here, ```--workers``` determines the number of instances of the server that will be created. In most cases, 1 will work just fine.

And you can visit the website by going to https://127.0.0.1:8000 in your web browser.

You will see a untrusted certificate message in most modern browsers. For this site (and this site only), you may ignore this warning and proceed to the site.

On subsequent runs, you only need to run:

    vagrant up
    vagrant ssh
    python manage.py runserver [::]:8000


# Setup with Heroku

Every PR should be that does something substantial (i.e. not a README change) must be accompanied with a live demo of the platform. To spin up your own heroku instance, you can sign up for an account for free and follow instructions found [here](https://devcenter.heroku.com/articles/git).

After setting up your own heroku instance, setup the build-packs for the instance by executing below commands in same order:

    heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-python.git
    heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-nodejs.git

To verify build-packs are setup correctly, execute below replacing <app-name>:

    heroku buildpacks --app <app-name>
    
This should output build-pack URLs as below in same order (nodejs should appear first compared to python): 

    === Buildpack URLs
    1. https://github.com/heroku/heroku-buildpack-nodejs.git
    2. https://github.com/heroku/heroku-buildpack-python.git

Use this command to deploy your branch to that instance.
    
    git push heroku yourbranch:master


