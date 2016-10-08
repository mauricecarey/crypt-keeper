from yaml import load
import logging
from .settings import CONFIGURATION_FILE_NAME

log = logging.getLogger(__name__)


class Configuration(object):
    def __init__(self, filename=None):
        self.config = {}
        if filename:
            try:
                self.config = load(open(filename, 'r', encoding='utf-8'))
                if not self.config:
                    self.config = {}
            except IOError:
                log.warning('Could not load configuration from file "%s". Will use defaults.')

    def __str__(self):
        return '%s' % self.config

    def get(self, key, default=None):
        return self.config.get(key, default=default)

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

CONFIGURATION = Configuration(CONFIGURATION_FILE_NAME)
