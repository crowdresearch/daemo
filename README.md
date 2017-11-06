# Daemo - Stanford Crowd Research Collective


This is a Django 1.11 app using a Postgres database 9.5+.

## Setup

[Please follow the GitHub tutorial](http://crowdresearch.stanford.edu/w/index.php?title=BranchingStrategy) to setup the repository.

If you are on Windows or want a simpler (automatic) setup process, please try the instructions in the [Setup with Vagrant](#setup-with-vagrant) section. Solutions to common errors can found on the [FAQ page](http://crowdresearch.stanford.edu/w/index.php?title=FAQs)

#### Databases
Install [Postgres](http://postgresapp.com/) 9.5+. If you have a Mac, we recommend using [Homebrew](http://brew.sh/). To install Postgres on a Mac using Homebrew:

    bash> brew install postgresql
    bash> brew services start postgresql
    bash> createdb

Create a new database:

    bash> psql
    psql> CREATE DATABASE crowdsource_dev ENCODING 'UTF8';

Create a `local_settings.py` file in the project root folder by copying `local_settings_default.py` and configure it to connect to your local Postgres database:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "crowdsource_dev"
        }
    }

Install [Redis](http://redis.io/download) key-value store used for managing sessions, cache and web-sockets support. To install Redis on a Mac:

    bash> brew install redis
    bash> brew services start redis

#### Backend Dependencies
Make sure you have [Python](https://www.python.org/downloads/) installed. Test this by opening a command line terminal and typing `python'.

Install [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html) to manage a local setup of your python packages:

    bash> pip install virtualenv

Go into the directory with the checkout of the code and create the Python virtual environment:

    bash> virtualenv venv

Source the virtual environment, install dependencies, and migrate the database:

    bash> source venv/bin/activate
    bash> pip install -r local_requirements.txt
    bash> python manage.py migrate

#### Frontend Dependencies
Install node.js. On a Mac:

    bash> brew install node

For Ubuntu or Debian:

    bash> sudo apt-get update
    bash> sudo apt-get install nodejs nodejs-legacy npm

Now, you can install the dependencies, which are managed by a utility called Bower:

    bash> npm install -g bower
    bash> npm install
    bash> bower install

To edit CSS using SASS, install SASS. Assuming you have Rails installed, which it is on every Mac:

    bash> sudo gem install sass

If there are no errors, you are ready to run the app from your local server:

    bash> python manage.py runserver

#### Grunt Toolchain with LiveReload
As an alternative, using grunt toolchain, you can start the server as below.
This will auto-compile SCSS using [LibSass](http://libsass.org/) and reload when changes happen for frontend.
For LiveReload, please visit [how do I install Live Reload and use the browser extensions](http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-) for your browser.
Pep8 styling issues will be identified for any python script modifications and notified in console.
Port 8000 is used by default. If it is already in use, please modify it in Gruntfile.js

    bash> grunt serve

#### uWSGI and Web-Sockets Support
Create a `uwsgi-dev.ini` file in the project root folder by copying `uwsgi-dev-default.ini`
If there are no errors, you are ready to run the app from your local server instead of the ```runserver``` command above:

    bash> uwsgi uwsgi-dev.ini

#### HTTPS mode
To start it, first disable http mode in `uwsgi-dev.ini` by adding `;` in front of

    http-socket = :8000


Unfortunately macOS got rid of the openSSL certificates needed for HTTPS, so you need to recompile the uwsgi with them included:

    cd /usr/local/include
    ln -s ../opt/openssl/include/openssl .
    pip uninstall gevent uwsgi
    pip install gevent
    C_INCLUDE_PATH=/usr/local/opt/openssl/include LIBRARY_PATH=/usr/local/opt/openssl/lib/ pip install uwsgi --no-binary :all:

Now, ``cd`` back to the main directory and use this command instead of the ```runserver``` command above:

    bash> uwsgi uwsgi-dev.ini -H /path/to/your/virtualenv

This uses the ```uwsgi``` server, which is used in production as well.


#### Background Jobs with Celery
To run celery locally: `celery -A csp worker -l info -B`



