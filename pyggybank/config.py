from pathlib import Path
import ruamel.yaml as yaml


CONFIG_DIR = Path.home() / '.config' / 'pyggybank'
CONFIG_FILE = CONFIG_DIR / 'config.yml'

# TODO: Duplicated in pygs
DEFAULT_ACCOUNTS_FILE = CONFIG_DIR / 'accounts.encrypted.yml'


# NOTE: We are depending on ordered configs as a result of 
# https://docs.python.org/3.6/whatsnew/3.6.html#new-dict-implementation.

if CONFIG_FILE.exists():
    with CONFIG_FILE.open('r') as fh:
        CONFIG = yaml.safe_load(fh)
else:
    CONFIG = {}
