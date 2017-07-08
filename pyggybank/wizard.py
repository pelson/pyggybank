import copy
import subprocess

from . import gpgconfig
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import print_tokens
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token

from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.interface import AbortAction
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory, AutoSuggest, Suggestion

from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt

import ruamel.yaml as yaml
from . import core
from . import config

providers = {}
for cls in core.Provider.__subclasses__():
    for name in cls.names:
        providers[name] = cls


test_style = style_from_dict({
        Token.Toolbar: '#ffffff bg:#333333',
        })


class ProviderValidator(Validator):
    def validate(self, document):
        text = document.text

        if text not in providers:
           raise ValidationError(message='"{}" is not a valid provider.'.format(text), cursor_position=len(text))

# Create a stylesheet.
style = style_from_dict({
        Token.Hello: '#ff0066',
        Token.World: '#44ff44 italic',
        Token.Bold: 'bold',
        })


def configure_provider():
    def get_bottom_toolbar_tokens(cli):
        return [(Token.Toolbar, ' Provider not in the list? Check out https://github.com/pelson/pyggybank.')]
    
    history = InMemoryHistory()
    [history.append(provider) for provider in providers]

    provider_completer = WordCompleter(providers, ignore_case=True, match_middle=True)

    # Make a list of (Token, text) tuples.
    tokens = [(Token.Bold, '\nSelect an internet banking provider to configure\n')]
    print_tokens(tokens, style=style)

    provider = prompt('Provider: ', completer=provider_completer,
                  complete_while_typing=True,
                  get_bottom_toolbar_tokens=get_bottom_toolbar_tokens,
                  style=test_style, validator=ProviderValidator(),
                  )

    tokens = [(Token.Bold, '\nConfiguring your {} account.\n'.format(provider))]
    print_tokens(tokens, style=style)
    cls = providers[provider]
    config = {'provider': provider}
    for attr in cls.attributes:
        attr_val = prompt('{}: '.format(attr), is_password=True)
        config[attr] = attr_val
    cls.validate_config(config)
    
    return config


from contextlib import contextmanager


def cat_account(accounts_file=config.DEFAULT_ACCOUNTS_FILE):
    accounts_file = Path(accounts_file)
    if not accounts_file.exists():
        print("Accounts file doesn't exist.")
    else:
        config = gpgconfig.decrypt_config(accounts_file)
        print(yaml.dump(config, indent=1, default_flow_style=False))
from pathlib import Path

@contextmanager
def _ctx_add_account(acc_file=config.DEFAULT_ACCOUNTS_FILE):
    acc_file = Path(acc_file)
    if not acc_file.exists():
        # Pick an identity, and write the basic config. We can then add to it
        # iteratively without concern for our ability to write with gnupg.
        ident = gpgconfig.select_gpg_id()
        config = {'gpg-ids': [ident]}
        gpgconfig.write_encrypted_config(acc_file, config)

    else:
        # First, let's read from the file to ensure we have access to decrypt it.
        # If we can, we will have the ability to write it back.
        config = gpgconfig.decrypt_config(acc_file)    

    # TODO: Add a test. This *IS* needed.
    config_orig = copy.deepcopy(config.copy)

    # Yield so that the context can be passed back to the caller, before
    # ultimately saving the (potentially) modified config.
    yield config

    print('orig', config_orig == config)
    if config_orig != config:
        gpgconfig.write_encrypted_config(acc_file, config)
    
        tokens = [(Token.Bold, 'Wrote config to: '), (Token.Regular, '{}\n'.format(acc_file))]
        print_tokens(tokens, style=style)


def add_account(new_account, acc_file=config.DEFAULT_ACCOUNTS_FILE):
    with _ctx_add_account(acc_file) as config:
        # TODO: Use the account validation functions.
        config.setdefault('accounts', []).append(new_account)


def wizard(accounts_file=config.DEFAULT_ACCOUNTS_FILE):
    with _ctx_add_account(accounts_file) as config:
        new_account = configure_provider()
        config.setdefault('accounts', []).append(new_account)


if __name__ == '__main__':
    wizard()
