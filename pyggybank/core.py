import copy
import logging


class InvalidProviderConfig(ValueError):
    pass


class attr(object):
    def __init__(self, name, alias=None, aliases=None):
        self.name = name
        self.aliases = []
        if alias:
            self.aliases.append(alias)
        if aliases:
            self.aliases.extend(aliases)

    @property
    def names(self):
        return [self.name] + self.aliases

    def from_config(self, config, remove=False):
        """
        Return the value of this attr instance within the given dictionary.

        Parameters
        ----------
        config : dict
            The config from which to take this attribute
        remove : bool
            Whether to remove the attribute from the given config, or whether to
            keep it. (default: False)

        Examples
        --------

        >>> f = attr('foo', alias='f')

        >>> f.from_config({'a': 1, 'f': 2})
        2

        >>> f.from_config({'a': 1, 'foo': 2})
        2

        >>> f.from_config({'a': 1, 'foo': 2, 'f': 3})
        Traceback (most recent call last):
        ...
        pyggybank.core.InvalidProviderConfig: Duplicate config item for "foo"...

        >>> f.from_config({'a': 1})
        Traceback (most recent call last):
        ...
        pyggybank.core.InvalidProviderConfig: No config item for "foo"

        """
        matching = [name for name in self.names if name in config]

        if remove:
            getter = config.pop
        else:
            getter = config.get

        values = [getter(key) for key in matching]

        # If duplicate information provided, but it is identical, let the
        # config through.
        if len(matching) > 1 and not all(values[0] == value
                                         for value in values[1:]):
            raise InvalidProviderConfig(
                'Duplicate config item for "{}". Got "{}"'
                ''.format(self.name, ', '.join(matching)))

        elif not matching:
            raise InvalidProviderConfig(
                'No config item for "{}"'.format(self.name))

        return values[0]



class Schema:
    def __init__(self, provider_names, provider_attrs):
        self.provider_names = provider_names
        self.provider_attrs = provider_attrs
        # TODO: Validate the schema (in case the provider is weirdly configured
        # or the attributes have name collisions).
        # Including: test attr.name and aliases don't collide with one another.

    def sanitise(self, config):
        if not hasattr(config, 'keys'):
            raise InvalidProviderConfig("Config isn't dict-like.")

        keys = set(config.keys())

        if 'provider' not in config:
            raise InvalidProviderConfig('"provider" is missing from the config')
        if config['provider'] not in self.provider_names:
            raise InvalidProviderConfig('"{}" is an invalid provider name'
                                        ''.format(config.get('provider')))

        sanitised = {'provider': config['provider']}

        config = copy.deepcopy(config)
        for provider_attr in self.provider_attrs:
            if not isinstance(provider_attr, attr):
                provider_attr = attr(provider_attr)
            config_attr = provider_attr.from_config(config, remove=True)
            sanitised[provider_attr.name] = config_attr

        remaining = sorted(set(config.keys()) - {'provider'})
        if remaining:
            raise InvalidProviderConfig(
                'The following config items are not allowed: {}'
                ''.format(', '.join(remaining))
            )
        return sanitised


class Credentials(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __getattr__(self, item):
        if item in self:
            return item[self]
        else:
            raise AttributeError('{} has not attribute {}'
                                 ''.format(self.__class__.__name__, item))


class Provider:
    attributes = []
    names = []
    domain = ''

    @classmethod
    def validate_config(cls, config):
        if not hasattr(config, 'keys'):
            raise InvalidProviderConfig("Config isn't dict-like.")

        keys = set(config.keys())
        cls_attrs = set(cls.attributes) | set(['provider'])
        if config.get('provider') not in cls.names:
            raise InvalidProviderConfig('The {} class does not provide {}'.format(config.get('provider')))

        missing = ', '.join(cls_attrs - keys)
        if missing:
            raise InvalidProviderConfig('Config items missing: {}'.format(missing))
        not_allowed = ', '.join(keys - cls_attrs)
        if not_allowed:
            raise InvalidProviderConfig('The following config items '
                                        'are not allowed: {}'.format(not_allowed))
        return True

    @classmethod
    def schema(cls):
        """Return the schema for this provider."""
        # Allow a provider the possibility of overriding the
        # Schema (type and/or instance).
        if isinstance(cls.attributes, Schema):
            schema = cls.attributes
        else:
            schema = Schema(cls.names, cls.attributes)
        return schema

    @classmethod
    def providers(cls):
        """Return a dictionary mapping provider name to class."""
        providers = {}
        for klass in cls.__subclasses__():
            for name in klass.names:
                if name in providers:
                    raise ValueError('Provider name collision for "{}" found '
                                     'between {} and {}.'
                                     ''.format(name, klass, providers[name]))
                providers[name] = klass
        return providers

    @classmethod
    def from_config(cls, config):
        """Given an account config, return a provider instance."""
        providers = cls.providers()
        provider_name = config.get('provider', None)
        if provider_name is None:
            raise ValueError('')
        provider = providers.get(provider_name, None)
        if provider is None:
            raise ValueError('')
        return provider.init_from_config(config)

    @classmethod
    def init_from_config(cls, config):
        """Instantiate the provider with the given config."""
        # TODO: Supply the config minus the credentials (e.g. nice-name).
        return cls()

    @classmethod
    def config_schema(cls):
        """Manufacture the config schema for this provider."""
        schema = Schema(cls.attributes)
        return schema

    def prepare_credentials(self, config):
        """Turn the given config into authentication credentials."""
        return Credentials(config)

    def authenticate(self, browser, credentials):
        """Login to the internet banking session."""
        pass

    def logout(self, browser):
        """Logout of the internet banking session."""
        pass

    def balances(self, browser):
        """Return a summary of all accounts."""
        # NOTE: Must ensure to go to the right page as the first action of
        # this method.

    def transactions(self, browser):
        """Return transactions for all accounts."""

    @property
    def log(self):
        """A pre-configured logger that can be used to log progress/debug."""
        if not hasattr(self, '_log'):
            log = logging.getLogger(self.__class__.__name__)
            logging.basicConfig()
            # TODO: Make configurable.
            log.setLevel(logging.INFO)
            self._log = log
        return self._log


from . import providers
