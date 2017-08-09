"""
These integration tests exist solely to test the interaction between pyggybank and GPG on the CLI.
All attempts should be made to avoid extending these tests in preference for unit tests of the functions
themselves (where necessary, mocking out the GPG interactions).

TODO: It would be great to bring these tests into the pyggybank.test module, and marking them as
full-blown integration tests.

"""

import pexpect
import sys
import os
import shutil
from pathlib import Path


gpg_vn = 2


def test_gpg_new_key_prompt():
    global gpg_vn

    # Check that pyggybank drops us into the gpg keygen prompt if we don't have any keys

    tmp = Path('tmp')
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()

    child = pexpect.spawnu('pyggybank wizard --gpg-home={}'.format(tmp))
#    child.logfile = os.fdopen(sys.stdout.fileno(), 'w')

    # We just want to check that we have initiated the gpg wizard correctly. The details aren't important.

    newer_gpg = True

    try:
        child.expect('Your selection?', timeout=1)
        child.sendline('1')
        child.expect('What keysize do you want?', timeout=1)
        child.sendline('2048')
        newer_gpg = False
        gpg_vn = 1
        child.expect('key expires in n years', timeout=1)
        child.sendline('0')
    except pexpect.exceptions.TIMEOUT:
        pass

    if newer_gpg:
        child.expect('Real name:')
        child.sendline('Testing Real Me')

        child.expect('Email address:')
        child.sendline('test@example.com')

        child.expect('\(O\)kay\/\(Q\)uit\?')

    child.close()

    # Let's get a newline afterwards.
    assert True
    print()


def test_gpg_no_agent():
    # Check the pyggybank behaviour when the gpg key hasn't been unlocked
    # (i.e. the gpg-agent is fresh)
    gpghome = Path(__file__).parent/'gpg'
    accounts_file = Path('accounts.encrypted.{}.yml'.format(gpg_vn))

    if gpg_vn < 2:
        raise RuntimeError('Cant yet handle older gpg.')

    if accounts_file.exists():
        accounts_file.unlink()
    child = pexpect.spawnu('pyggybank wizard --gpg-home={} --accounts-file={}'.format(gpghome, accounts_file))
  #  child.logfile = os.fdopen(sys.stdout.fileno(), 'w')

    child.expect('GPG identity would you like to encrypt with\?', timeout=5)
    child.sendline('Testing Name <test@example.com>')

    child.expect('Provider:')
    child.sendline('Test provider')

    child.expect('User ID')
    child.sendline('abcdef')

    child.expect('password')
    child.sendline('123456')

    child.expect('Wrote config')

    # --------

    child = pexpect.spawnu('pyggybank accounts --accounts-file={} --gpg-home={}'.format(accounts_file, gpghome))
    #child.logfile = os.fdopen(sys.stdout.fileno(), 'w')

    # Will only be called if gpg-agent isn't running.
    child.expect('GPG passphrase\:')
    child.sendline('Th15154T35t')

    child.expect('Test provider')

    # Let's get a newline afterwards.
    assert True
    print()

    

if __name__ == '__main__':
    test_gpg_new_key_prompt()
    test_gpg_no_agent()
