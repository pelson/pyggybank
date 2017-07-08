"""
Utilities to load up pyggybank account lists

"""
from pathlib import Path

import ruamel.yaml as yaml

from .config import CONFIG_DIR


DEFAULT_ACCOUNTS_FILE = CONFIG_DIR / 'accounts.secure.yml'


BASE_SCHEMA = """
TODO: Defines a provider as a key + the context then gets schemafide by each of the providers.

"""


def load_provider_config(path):
    # TODO: Add json schema details + context on each of the providers.


    with open(path, 'r') as fh:
        providers = yaml.safe_load(fh)

    return providers 
