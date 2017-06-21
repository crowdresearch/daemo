#!/bin/sh

source /usr/local/bin/virtualenvwrapper.sh

Activate () {
  workon crowd
}

Activate
python manage.py runserver
