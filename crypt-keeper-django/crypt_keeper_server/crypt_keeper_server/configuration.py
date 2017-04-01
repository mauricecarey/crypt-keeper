#   Copyright 2017 Maurice Carey
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from yaml import load, dump
from warnings import warn
from logging import getLogger

log = getLogger('crypt-keeper.' + __name__)


class Configuration(object):
    def __init__(self, filename=None):
        self.config = {}
        self.filename = filename
        self.reload_config()

    def reload_config(self):
        if self.filename:
            try:
                self.config = load(open(self.filename, 'r', encoding='utf-8'))
                if not self.config:
                    self.config = {}
            except IOError as e:
                log.warning('Could not load configuration from file "%s". Will use defaults.')
                raise e

    def write_config(self):
        if self.filename:
            with open(self.filename, 'w') as file:
                file.write(dump(self.config, default_flow_style=False))
        else:
            err = 'No filename defined.'
            log.error(err)
            warn(err)

    def __str__(self):
        return '%s' % self.config

    def get(self, key, default=None):
        return self.config.get(key, default=default)

    def set(self, key, value):
        key_list = key.split(':')
        config = self.config
        for k in key_list[:-1]:
            if k not in config:
                config[k] = {}
            config = config.get(k)
        k = key_list[-1:][0]
        config[k] = value

    @staticmethod
    def _lookup(dic, key, *keys):
        if keys:
            return Configuration._lookup(dic.get(key, {}), *keys)
        return dic.get(key)

    def lookup(self, key, default=None):
        key_list = key.split(':')
        val = Configuration._lookup(self.config, *key_list)
        if val:
            return val
        return default
