include:
  - docker
  - docker.containers
  - apache.mod_wsgi
  - apache.vhosts.standard

# sudo apt-get install python3-dev
# sudo apt-get install python-virtualenv

python-environment:
  pkg.installed:
    - pkgs:
      - python3-dev
      - python-virtualenv

# sudo apt-get install libxml2-dev libxslt1-dev
# sudo apt-get install zlib1g-dev

lxml-support-packages:
  pkg.installed:
    - pkgs:
      - libxml2-dev
      - libxslt1-dev
      - zlib1g-dev

psycopg2-support-packages:
  pkg.installed:
    - pkgs:
      - libpq-dev

# cd /srv/crypt-keeper.com
# sudo git clone https://mcarey@bitbucket.org/prometheussoftware/crypt-keeper.git
# sudo chown -R vagrant .

crypt-keeper-dir:
  file.directory:
    - name: /srv/crypt-keeper.com
    - user: vagrant
    - group: www-data
    - mode: 775
    - recurse:
      - user
      - group
      - mode
    - watch:
      - git: crypt-keeper-source
      - cmd: crypt-keeper-migrate
      - file: ck-prod-settings

crypt-keeper-source:
  file.directory:
    - name: /srv/crypt-keeper.com
    - user: vagrant
    - group: www-data
    - mode: 775
  git.latest:
    - name: git@bitbucket.org:prometheussoftware/crypt-keeper.git
    - target: /srv/crypt-keeper.com/crypt-keeper
    - force_clone: True
    - force_reset: True
    - user: vagrant
    - identity: /srv/ssh-key/id_rsa
    - require:
      - file: crypt-keeper-source

# set-permissions:
#   cmd.run:
#     - name: chown -R vagrant:www-data

# cd crypt-keeper/crypt-keeper-django/
# sudo virtualenv -p `which python3` env
# source env/bin/activate
# sudo pip install -r requirements.txt

crypt-keeper-log:
  file.directory:
    - name: /var/log/crypt-keeper
    - user: vagrant
    - group: www-data
    - mode: 775

crypt-keeper-django-log-file:
  file.managed:
    - name: /var/log/crypt-keeper/django.log
    - user: vagrant
    - group: www-data
    - mode: 775

crypt-keeper-log-file:
  file.managed:
    - name: /var/log/crypt-keeper/debug.log
    - user: vagrant
    - group: www-data
    - mode: 775

crypt-keeper-virtualenv:
  virtualenv.managed:
    - name: /srv/crypt-keeper.com/env
    - python: /usr/bin/python3
    - requirements: /srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/requirements.txt
    - user: vagrant
    - require:
      - pkg: python-environment
      - pkg: lxml-support-packages
      - pkg: psycopg2-support-packages
      - git: crypt-keeper-source
      - file: crypt-keeper-log
      - file: crypt-keeper-django-log-file
      - file: crypt-keeper-log-file
    - require_in:
      - pkg: apache

# python manage.py migrate

ck-prod-settings:
  file.managed:
    - name: /srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server/prod_settings.py
    - source: salt://ck/files/prod_settings.py
    - user: vagrant
    - template: jinja

crypt_keeper_config.yml:
  file.managed:
    - name: /srv/crypt-keeper.com/crypt_keeper_config.yml
    - source: salt://ck/files/crypt_keeper_config.yml
    - user: vagrant
    - template: jinja

crypt-keeper-migrate:
  cmd.run:
    - name: /srv/crypt-keeper.com/env/bin/python manage.py migrate
    - cwd: /srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/crypt_keeper_server
    - env: 
      - DJANGO_SETTINGS_MODULE: 'crypt_keeper_server.prod_settings'
    - user: vagrant
    - require_in:
      - pkg: apache
    - require:
      - virtualenv: crypt-keeper-virtualenv
    - watch:
      - file: ck-prod-settings
      - file: crypt_keeper_config.yml

crypt-keeper-collectstatic:
  cmd.run:
    - name: /srv/crypt-keeper.com/env/bin/python manage.py collectstatic --noinput
    - cwd: /srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/crypt_keeper_server
    - env: 
      - DJANGO_SETTINGS_MODULE: 'crypt_keeper_server.prod_settings'
    - user: vagrant
    - require_in:
      - pkg: apache
    - require:
      - virtualenv: crypt-keeper-virtualenv
      - file: crypt_keeper_config.yml
    - watch:
      - file: ck-prod-settings

# hack to make sure py3 wsgi gets installed before reload so apache service doesn't fail.

wsgi-before-reload:
  cmd.run:
    - name: echo ''
    - require_in:
      - module: apache-reload
      - service: apache
    - require:
      - pkg: mod_wsgi

envvars:
  file.append:
    - name: /etc/apache2/envvars
    - text: |
        export DJANGO_SETTINGS_MODULE='crypt_keeper_server.prod_settings'
