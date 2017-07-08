class InvalidProviderConfig(ValueError):
    pass


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

from . import providers
