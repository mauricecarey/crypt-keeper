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

### Run Django tests
The following commands can be used to run the Django tests:

    cd crypt-keeper-django/crypt_keeper_server
    python manage.py test

### Generating coverage reports
The following commands can be used to generate a coverage report:

    cd crypt-keeper-django/crypt_keeper_server
    coverage run --source='.' manage.py test
    coverage report

### Running simple SMTP server
 Running a simple SMTP server to test email sending:
 
    python -m smtpd -n -c DebuggingServer localhost:1025
    
Add the following to SETTINGS file:

    if DEBUG:
        EMAIL_HOST = 'localhost'
        EMAIL_PORT = 1025
        EMAIL_HOST_USER = ''
        EMAIL_HOST_PASSWORD = ''
        EMAIL_USE_TLS = False
        DEFAULT_FROM_EMAIL = 'crypt-keeper@example.com'

