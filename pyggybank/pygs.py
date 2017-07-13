"""
Utilities to load up pyggybank account lists

"""
from pathlib import Path

import ruamel.yaml as yaml

from .config import CONFIG_DIR
from . import core


DEFAULT_ACCOUNTS_FILE = CONFIG_DIR / 'accounts.secure.yml'


BASE_SCHEMA = """
TODO: Defines a provider as a key + the context then gets schemafide by each of the providers.

"""


def load_provider_config(path):
    # TODO: Add json schema details + context on each of the providers.


    with open(path, 'r') as fh:
        return load_provider_config_from_buffer(fh)


def load_provider_config_from_buffer(content):
    providers = yaml.safe_load(content)
    if not isinstance(providers, dict):
        raise TypeError('The config content should contain a dictionary at the '
                        'top level, got {}.'.format(type(providers)))
    if 'accounts' not in providers:
        raise ValueError('The accounts list was not defined in the config.')
    if not isinstance(providers['accounts'], list):
        raise ValueError('"accounts" config item should be a list of '
                         'provider dictionaries')

    for account in providers['accounts']:
        provider = core.Provider.pick_provider(account)
        provider.schema().sanitise(account)

    return providers
