{% import_yaml "data/ck.sls" as ck %}
apache:
  lookup:
    mod_wsgi: libapache2-mod-wsgi-py3
  sites:
    {{ ck.crypt_keeper.url }}:
      enabled: True
      template_file: salt://apache/vhosts/standard.tmpl
      LogLevel: debug
      Alias:
        /static/:
          {{ ck.crypt_keeper.base_dir }}/static/
      Directory:
        default:
          Options: False
          AllowOverride: False
          Formula_Append: |
            <Files crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server/wsgi.py>
            Require all granted
            </Files>
        {{ ck.crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server:
          Formula_Append: |
            <Files wsgi.py>
            Require all granted
            </Files>
        {{ ck.crypt_keeper.base_dir }}/static:
          Options: False
        {{ ck.crypt_keeper.base_dir }}/media:
          Options: False
      Formula_Append: |
        WSGIDaemonProcess {{ ck.crypt_keeper.url }} python-home={{ ck.crypt_keeper.virtual_env_location }} python-path={{ ck.crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/crypt_keeper_server
        WSGIProcessGroup {{ ck.crypt_keeper.url }}
        WSGIScriptAlias / {{ ck.crypt_keeper.base_dir }}/crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server/wsgi.py process-group={{ ck.crypt_keeper.url }}
        WSGIPassAuthorization On
