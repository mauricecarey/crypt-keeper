{% from "ck/map.jinja" import crypt_keeper with context %}

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

# cd {{ crypt_keeper.base_dir }}
# sudo git clone https://mcarey@bitbucket.org/prometheussoftware/crypt-keeper.git
# sudo chown -R {{ crypt_keeper.install_username }} .

crypt-keeper-dir:
  file.directory:
    - name: {{ crypt_keeper.base_dir }}
    - user: {{ crypt_keeper.install_username }}
    - group: {{ crypt_keeper.apache_username }}
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
    - name: {{ crypt_keeper.base_dir }}
    - user: {{ crypt_keeper.install_username }}
    - group: {{ crypt_keeper.apache_username }}
    - mode: 775
  git.latest:
    - name: git@bitbucket.org:prometheussoftware/crypt-keeper.git
    - target: {{ crypt_keeper.base_dir }}/crypt-keeper
    - force_clone: True
    - force_reset: True
    - user: {{ crypt_keeper.install_username }}
    - identity: {{ crypt_keeper.git_identity }}
    - require:
      - file: crypt-keeper-source

# set-permissions:
#   cmd.run:
#     - name: chown -R {{ crypt_keeper.install_username }}:{{ crypt_keeper.apache_username }}

# cd crypt-keeper/crypt-keeper-django/
# sudo virtualenv -p `which python3` env
# source env/bin/activate
# sudo pip install -r requirements.txt

crypt-keeper-log:
  file.directory:
    - name: {{ crypt_keeper.log_dir }}
    - user: {{ crypt_keeper.install_username }}
    - group: {{ crypt_keeper.apache_username }}
    - mode: 775

crypt-keeper-django-log-file:
  file.managed:
    - name: {{ crypt_keeper.log_dir }}/{{ crypt_keeper.django_log_name }}
    - user: {{ crypt_keeper.install_username }}
    - group: {{ crypt_keeper.apache_username }}
    - mode: 775

crypt-keeper-log-file:
  file.managed:
    - name: {{ crypt_keeper.log_dir }}/{{ crypt_keeper.log_name }}
    - user: {{ crypt_keeper.install_username }}
    - group: {{ crypt_keeper.apache_username }}
    - mode: 775

crypt-keeper-virtualenv:
  virtualenv.managed:
    - name: {{ crypt_keeper.virtual_env_location }}
    - python: /usr/bin/python3
    - requirements: {{ crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/requirements.txt
    - user: {{ crypt_keeper.install_username }}
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
    - name: {{ crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server/prod_settings.py
    - source: salt://ck/files/prod_settings.py
    - user: {{ crypt_keeper.install_username }}
    - template: jinja

crypt_keeper_config.yml:
  file.managed:
    - name: {{ crypt_keeper.base_dir }}/crypt_keeper_config.yml
    - source: salt://ck/files/crypt_keeper_config.yml
    - user: {{ crypt_keeper.install_username }}
    - template: jinja

crypt-keeper-migrate:
  cmd.run:
    - name: {{ crypt_keeper.virtual_env_location }}/bin/python manage.py migrate
    - cwd: {{ crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/crypt_keeper_server
    - env: 
      - DJANGO_SETTINGS_MODULE: 'crypt_keeper_server.prod_settings'
    - user: {{ crypt_keeper.install_username }}
    - require_in:
      - pkg: apache
    - require:
      - virtualenv: crypt-keeper-virtualenv
    - watch:
      - file: ck-prod-settings
      - file: crypt_keeper_config.yml

crypt-keeper-collectstatic:
  cmd.run:
    - name: {{ crypt_keeper.virtual_env_location }}/bin/python manage.py collectstatic --noinput
    - cwd: {{ crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/crypt_keeper_server
    - env: 
      - DJANGO_SETTINGS_MODULE: 'crypt_keeper_server.prod_settings'
    - user: {{ crypt_keeper.install_username }}
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
