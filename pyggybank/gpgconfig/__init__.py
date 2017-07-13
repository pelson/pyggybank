import subprocess

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

from ruamel import yaml

import gnupg
from pprint import pprint

import logging

log = logging.getLogger(__name__)
logging.basicConfig()

import pyggybank.config as cfg


def gpg_init():
    return gnupg.GPG(use_agent=True, gnupghome=cfg.CONFIG.get('gpg-home', None))


def assert_gpg_keys(gpg, private=False):
    """
    Assert at least one GPG key exists, otherwise drop to the GPG CLI.

    """
    while not gpg.list_keys(private):
        print('No private keys found. Sending you to the gpg executable now...')
        extra_args = []
        gpg_home = cfg.CONFIG.get('gpg-home', None)
        if gpg_home:
            extra_args.extend(['--homedir', gpg_home])
        p = subprocess.Popen([gpg.gpgbinary, '--gen-key'] + extra_args)
        p.wait()


from prompt_toolkit.validation import Validator, ValidationError
from six import string_types

from prompt_toolkit.contrib.validators.base import SentenceValidator

from prompt_toolkit.completion import Completer, Completion


def select_gpg_id():
    gpg = gpg_init()

    assert_gpg_keys(gpg, private=True)

    ids = []
    for key in gpg.list_keys(True):
        ids.extend(key['uids'])
    ids = sorted(set(ids))

    ident_completer = WordCompleter(ids)

    tokens = [(Token.Regular, 'The following GPG identities have been found:\n  {}\n'.format('\n  '.join(ids)))]
    print_tokens(tokens)
    selected_id = prompt('Which GPG identity would you like to encrypt with? ',
                          completer=ident_completer, validator=SentenceValidator(ids, error_message='Invalid identity'),
                          complete_while_typing=True, )
    return selected_id


def write_encrypted_config(path, config):
    gpg = gpg_init()

    assert_gpg_keys(gpg)

    ids = config.get('gpg-ids', [])

    if not ids or not isinstance(ids, list):
        raise ValueError('gpg-ids must be a list of ids to use for encrypting the config.')

    message = yaml.dump(config, indent=1, default_flow_style=False)
    encrypted = gpg.encrypt(message, ids)

    if not encrypted.ok:
        log.warn(pprint(encrypted.__dict__))
        raise RuntimeError('Unable to encrypt the message.')

    with open(path, 'wb') as fh:
        fh.write(bytes(str(encrypted), 'utf-8'))


def decrypt_file(path, decryption_context="the config"):
    with open(path, 'rb') as fh:
        encrypted = fh.read()

    gpg = gpg_init()
    assert_gpg_keys(gpg, private=True)

    # Temporarily drop gnupg warnings for the first decryption.
    gpg_log = logging.getLogger('gnupg')
    level = gpg_log.level
    gpg_log.setLevel(logging.ERROR)

    # Decrypy, then re-enable the logging level.
    decrypted = gpg.decrypt(encrypted)
    gpg_log.setLevel(level)

    if not decrypted.ok:
        # It could be that we just need to unlock the gpg-agent.
        passphrase = prompt('Enter your GPG passphrase: ', is_password=True)
        decrypted = gpg.decrypt(encrypted, passphrase=passphrase)

    if not decrypted.ok:
        log.warn(pprint(decrypted.__dict__))
        raise RuntimeError(
            'Unable to decrypt {}. Are you able to decrypt with '
            '"{} --decrypt {}"?'.format(decryption_context,
                                        gpg.gpgbinary, path))
    return decrypted


def decrypt_config(path):
    decrypted = decrypt_file(path)
    config = yaml.safe_load(str(decrypted))
    return config


if __name__ == '__main__':
    ident = select_gpg_id()
    config = {'gpg-ids': [ident]}
#    write_encrypted_config('foo.enc.yml', config)

    config = decrypt_config('foo.enc.yml')
    pprint(config)
