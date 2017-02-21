test:
  file.managed:
    - name: /home/vagrant/test.txt
    - source: salt://test/files/home/vagrant/test.txt
    - template: jinja
    - makedirs: True
