import imp
import os


class ConfigError(KeyError):
    """Exception thrown when the requested key does not exist."""


class Config(object):
    """Has a dict-like interface with some handy subtilities regarding
    config management.

    """

    def __init__(self, env_prefix=None):
        self.env_prefix = env_prefix

        self.base_values = {}
        self.set_values = {}

    def __getitem__(self, name):
        try:
            return self.set_values[name]
        except KeyError:
            pass

        if self.env_prefix:
            try:
                return os.environ[self.env_prefix+name]
            except KeyError:
                pass

        try:
            return self.base_values[name]
        except KeyError:
            raise ConfigError(
                'The requested config value, {}, is not set.'.format(name))

    def __setitem__(self, name, value):
        self.set_values[name] = value

    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self.base_values[key] = getattr(obj, key)

    def from_pyfile(self, filename):
        d = imp.new_module('config')
        d.__file__ = filename
        with open(filename, mode='rb') as config_file:
            exec(compile(config_file.read(), filename, 'exec'), d.__dict__)

        self.from_object(d)
