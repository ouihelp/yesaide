import importlib.machinery
import importlib.util
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

    def get(self, name, default_value=None):
        try:
            return self.__getitem__(name)
        except ConfigError:
            return default_value

    def from_object(self, obj):
        for key in dir(obj):
            if key.isupper():
                self.base_values[key] = getattr(obj, key)

    def from_pyfile(self, filename):
        spec = importlib.machinery.ModuleSpec(
            'config',
            importlib.machinery.SourceFileLoader('config', filename),
            origin=filename,
        )
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        self.from_object(config)
