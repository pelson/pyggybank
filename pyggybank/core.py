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

        >>> f.from_config({'a': 1, 'foo': 2, 'f': 2})
        2

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

    def extract_credentials(self, config):
        """
        Take the credentials out of the given sanitised config.

        """
        new_config = {}
        credentials = {}
        for provider_attr in self.provider_attrs:
            if not isinstance(provider_attr, attr):
                provider_attr = attr(provider_attr)
            if not getattr(provider_attr, 'are_credentials', True):
                continue
            item = config.get(provider_attr.name, None)
            if item is not None:
                credentials[provider_attr.name] = item
                for name in provider_attr.aliases:
                    credentials[name] = item

        credentials = Credentials(credentials)
        return new_config, credentials


class Credentials(dict):
    def __getattr__(self, item):
        if item in self:
            return self[item]
        else:
            raise AttributeError('{} has not attribute {}'
                                 ''.format(self.__class__.__name__, item))


class ClassPropertyDescriptor:

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


class Provider:
    _attributes = []


    names = []
    domain = ''

    @classproperty
    def attributes(cls):
        attrs = []
        for attribute in self._attributes:
            if not isinstance(attribute, attr):
                attribute = attr(attribute)
            attrs.append(attribute)
        return attrs

    # @classmethod
    # def validate_config(cls, config):
    #     if not hasattr(config, 'keys'):
    #         raise InvalidProviderConfig("Config isn't dict-like.")
    #
    #     keys = set(config.keys())
    #     cls_attrs = set(cls.attributes) | set(['provider'])
    #     if config.get('provider') not in cls.names:
    #         raise InvalidProviderConfig(
    #             'The "{}" class does not provide "{}"'
    #             ''.format(cls.__name__, config.get('provider')))
    #
    #     missing = ', '.join(cls_attrs - keys)
    #     if missing:
    #         raise InvalidProviderConfig('Config items missing: {}'.format(missing))
    #     not_allowed = ', '.join(keys - cls_attrs)
    #     if not_allowed:
    #         raise InvalidProviderConfig('The following config items '
    #                                     'are not allowed: {}'.format(not_allowed))
    #     return True

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
    def pick_provider(cls, config):
        providers = cls.providers()
        provider_name = config.get('provider', None)
        if provider_name is None:
            raise ValueError('The provider was not defined in the account '
                             'config')
        provider = providers.get(provider_name, None)
        if provider is None:
            raise ValueError(
                'No provider found for "{}"'.format(provider_name))
        return provider

    @classmethod
    def from_config(cls, config):
        """
        Given an account config, return a provider instance and
        the Credentials.

        """
        provider = cls.pick_provider(config)
        schema = provider.schema()
        config = schema.sanitise(config)
        config, credentials = schema.extract_credentials(config)
        return provider.init_from_config(config), credentials

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
