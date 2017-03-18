# Vagrant Production Example

The vagrant example demonstrates installing Crypt-keeper using salt stack with a Postgres DB as backend. For a proper production install you'll also want redundant servers etc.

## Startup
Assuming you have cloned the Crypt-keeper repo to '~/source/crypt-keeper' be sure you have also initialized any needed submodules with:

    cd ~/source/crypt-keeper
    git submodule update --init

then:

    cd ~/source/crypt-keeper/crypt-keeper-vagrant/
    vagrant up

## Create user and setup AWS account
From the same directory as startup above:

    vagrant ssh
    cd /srv/crypt-keeper.local/crypt-keeper/crypt-keeper-django/crypt_keeper_server
    export DJANGO_SETTINGS_MODULE='crypt_keeper_server.prod_settings'
    /srv/crypt-keeper.local/env/bin/python manage.py createsuperuser
    /srv/crypt-keeper.local/env/bin/python manage.py initial_setup 'aws_access_key' --aws_secret_key 'key'
    sudo service apache2 restart

## Create hostname alias

Create an alias for the name crypt-keeper.local to point to your local host. This can work differently depending on the platform you are running but on my current Mac OSX I add:

    127.0.0.1 crypt-keeper.local

to the '/etc/hosts' file.

## Create API key for user

    open http://crypt-keeper.local:8081/admin

Login with the credentials you created in the last step. Then create an API key, which we will call 'test' for our example, associated with the user.

## Install the crypt-keeper client
For installation of the most current released version

    cd some/path/you/keep/virtualenvs/at
    virtualenv -p `which python3` some_env
    source some_env/bin/activate
    pip install py_crypt_keeper_client

or to install from the git repo for development:

    cd ~/source
    git clone git@bitbucket.org:prometheussoftware/py_crypt_keeper_client.git
    cd py_crypt_keeper_client
    virtualenv -p `which python3` env
    source env/bin/activate
    python setup.py develop


## Upload a document

    ckc -u username --url http://crypt-keeper.local:8081/api/v1/document_service -a test upload test.txt

## Download a document

    ckc -u username --url http://crypt-keeper.local:8081/api/v1/document_service -a test download -f temp.txt 94046d4b-fc35-46e9-af4d-35659cba48e6
