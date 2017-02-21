{% set node_type = salt['grains.get']('node_type', '') %}
base:
  '*':
    - test

{% if node_type %}
  'node_type:{{ node_type }}':
    - match: grain
    - {{ node_type }}
{% endif %}
