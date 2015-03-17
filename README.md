# RODRIGUES - a web based radio telescope calibration simulation

## Installation

### On a fresh Ubuntu 14.04 machine

First make sure you have the latest docker (>= 1.3) installed (not the default
Ubuntu docker.io package).

https://docs.docker.com/installation/ubuntulinux/#ubuntu-trusty-1404-lts-64-bit

run:

    $ sudo apt-get update
    $ sudo apt-get install -y python-pip git
    $ sudo pip install docker-compose
    $ git clone https://github.com/ska-sa/rodrigues && cd rodrigues

Copy the cyberska viewer license file into the checkout and name it `pureweb.lic`.

To start RODRIGUES:

    $ SECRET_KEY=secretkey docker-compose up

This will start a webserver on port 80. Replace `secretkey` with something secret and random, it
is used to create HTTP sessions.



There are more environment variables you may need to set:
 - **ALLOWED_HOST** (default: rodrigues.meqtrees.net)
 - **CYBERSKA_URI** (no default)
 - **ADMIN_EMAIL**
 - **DEBUG** set to true to enable debugging mode (default: off)


## Initialise DB

First time you run this app you need to create and populate the database

    $ docker-compose run worker python3 manage.py syncdb


## Development setup

You need:

   * Python 3
   * Python PIP (`$ sudo apt-get install python3-pip`)
   * RabbitMQ (`$ sudo apt-get install rabbitmq-server`)
   * postgres (`$ sudo apt-get install postgresql postgresql-server-dev-all`)


Now to install the required libraries run inside the rodrigues folder:

    $ pip3 install -r requirements.txt


First you need to inform Django that you want to use the development settings:

    $ export DJANGO_SETTINGS_MODULE=rodrigues.settings.development


Now you are ready to start the pipeline. To start the django server you first
need to populate the database:

    $ python3 ./manage.py syncdb


Now you can run a development webserver using:

    $ python3 ./manage.py runserver


To run the scheduled simulations you need to run a broker and celery worker:

    $ make broker &
    $ make worker &

