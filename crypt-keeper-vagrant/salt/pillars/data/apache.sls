apache:
  lookup:
    mod_wsgi: libapache2-mod-wsgi-py3
  sites:
    crypt-keeper.com:
      enabled: True
      template_file: salt://apache/vhosts/standard.tmpl
      LogLevel: debug
      Alias:
        /static/:
          /srv/crypt-keeper.com/static/
      Directory:
        default:
          Options: False
          AllowOverride: False
          Formula_Append: |
            <Files crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server/wsgi.py>
            Require all granted
            </Files>
        /srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server:
          Formula_Append: |
            <Files wsgi.py>
            Require all granted
            </Files>
        /srv/crypt-keeper.com/static:
          Options: False
        /srv/crypt-keeper.com/media:
          Options: False
      Formula_Append: |
        WSGIDaemonProcess crypt-keeper.com python-home=/srv/crypt-keeper.com/env python-path=/srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/crypt_keeper_server
        WSGIProcessGroup crypt-keeper.com
        WSGIScriptAlias / /srv/crypt-keeper.com/crypt-keeper/crypt-keeper-django/crypt_keeper_server/crypt_keeper_server/wsgi.py process-group=crypt-keeper.com
        WSGIPassAuthorization On
