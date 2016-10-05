# Crypt-Keeper Django Prototype Server
This project is being created simply to prototype the Crypt-Keeper service quickly, and will not implement the Dynamo backing store. Definitely not recommended for heavy traffic, but should be able to handle moderate traffic using Postgres or mysql data store.

## Installing

    cd crypt-keeper-django
    virtualenv -p `which python3` env
    pip install -r requirements.txt

## Running
For the first time:

    cd crypt-keeper-django
    cd crypt_keeper_server
    python manage.py migrate
    python manage.py createsuperuser

then:

    python manage.py runserver
