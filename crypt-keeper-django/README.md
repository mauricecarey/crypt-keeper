# Crypt-Keeper Django Prototype Server
This project is being created simply to prototype the Crypt-Keeper service quickly, and will not implement the Dynamo backing store. Definitely not recommended for heavy traffic, but should be able to handle moderate traffic using Postgres or mysql data store.

## Installing

    cd crypt-keeper-django
    virtualenv -p `which python3` env
    source env/bin/activate
    pip install -r requirements.txt
    cd crypt_keeper_server
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py initial_setup 'aws_access_key' --aws_secret_key key

## Running

    cd crypt-keeper-django/crypt_keeper_server
    python manage.py runserver

## Testing
To generate fixtures for testing use:

    python manage.py dumpdata
    
See [docs](https://docs.djangoproject.com/en/1.10/ref/django-admin/#dumpdata) for more info.
