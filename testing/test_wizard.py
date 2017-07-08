import pexpect
import sys
import os


def test_gpg_new_key_prompt():
    # Check that pyggybank drops us into the gpg keygen prompt if we don't have any keys

    child = pexpect.spawnu('pyggybank wizard --gpg-home=not_real')
    child.logfile = os.fdopen(sys.stdout.fileno(), 'w')

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
    from pathlib import Path
    gpghome = Path(__file__).parent/'gpg'
    accounts_file = Path('accounts.encrypted.yml')

    if accounts_file.exists():
        accounts_file.unlink()
    child = pexpect.spawnu('pyggybank wizard --gpg-home={} --accounts-file={}'.format(gpghome, accounts_file))
#    child.logfile = os.fdopen(sys.stdout.fileno(), 'w')

    child.expect('GPG identity would you like to encrypt with\?', timeout=2)
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
    child.logfile = os.fdopen(sys.stdout.fileno(), 'w')

    child.expect('GPG passphrase\:')
    child.sendline('Th15154T35t')

    child.expect('Test provider')

    # Let's get a newline afterwards.
    assert True
    print()

    

if __name__ == '__main__':
    #test_gpg_new_key_prompt()
    test_gpg_no_agent()
