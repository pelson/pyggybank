import argparse
import sys

import prompt_toolkit

from . import pygs
from . import config
from . import core

# An extension of argparse as defined by https://stackoverflow.com/a/26379693/741316
def set_default_subparser(self, name, args=None):
    """default subparser selection. Call after setup, just before parse_args()
    name: is the name of the subparser to call by default
    args: if set is the argument list handed to parse_args()

    , tested with 2.7, 3.2, 3.3, 3.4
    it works with 2.6 assuming argparse is installed
    """
    subparser_found = False
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:  # global help if no subparser
            break
    else:
        for x in self._subparsers._actions:
            if not isinstance(x, argparse._SubParsersAction):
                continue
            for sp_name in x._name_parser_map.keys():
                if sp_name in sys.argv[1:]:
                    subparser_found = True
        if not subparser_found:
            # insert default in first position, this implies no
            # global options without a sub_parsers specified
            if args is None:
                sys.argv.insert(1, name)
            else:
                args.insert(0, name)


argparse.ArgumentParser.set_default_subparser = set_default_subparser


class RepeatedOptionWithDefault(argparse.Action):
    # https://bugs.python.org/issue16399
    def __call__(self, parser, namespace, value, option_string=None):
        dest = getattr(namespace, self.dest, [])
        if dest is self.default:
            dest = []
        dest.append(value)
        setattr(namespace, self.dest, dest)


def accounts_cat(infile, accounts_file):
    from . import wizard as wizard_mod

    if infile is None or infile.isatty():
        # pyggybank accounts > foo.txt
        # pyggybank accounts

        infile = infile or sys.stdout
        sys.exit(wizard_mod.cat_account(infile, accounts_file=accounts_file))
    else:
        # pyggybank accounts < foo.txt
        content = infile.read()
        sys.exit(wizard_mod.write_account(content, accounts_file=accounts_file))


def main():
    parser = argparse.ArgumentParser(description='Get information from your internet banks')

    top_subparser = parser.add_subparsers()
    sp = top_subparser.add_parser('balance')
    sp.set_defaults(func=balance)

    visit_parser = top_subparser.add_parser('visit')
    visit_parser.set_defaults(func=visit)

    wizard_parser = top_subparser.add_parser('wizard')
    wizard_parser.set_defaults(func=wizard)
    accounts_parser = top_subparser.add_parser('accounts')
    import sys
    accounts_parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                                 default=sys.stdin if not sys.stdin.isatty() else None)

    accounts_parser.set_defaults(func=accounts_cat)

    # TODO: Should this just be controled by config, and not a CLI arg...?
    wizard_parser.add_argument('--gpg-home', dest='gpg_home', default=None)
    accounts_parser.add_argument('--gpg-home', dest='gpg_home', default=None)

    accounts_parser.add_argument(
            '--accounts-file',
            default=pygs.DEFAULT_ACCOUNTS_FILE,
            dest='accounts_file',
            help=('The accounts file to use (default: {})'
                  ''.format(pygs.DEFAULT_ACCOUNTS_FILE)))

    wizard_parser.add_argument(
            '--accounts-file',
            default=pygs.DEFAULT_ACCOUNTS_FILE,
            dest='accounts_file',
            help=('The accounts file to use (default: {})'
                  ''.format(pygs.DEFAULT_ACCOUNTS_FILE)))

    sp.add_argument(
            '--accounts',
            action=RepeatedOptionWithDefault,
            default=[pygs.DEFAULT_ACCOUNTS_FILE],
            dest='accounts_files',
            help=('The accounts file to use (default: {})'
                  ''.format(pygs.DEFAULT_ACCOUNTS_FILE)))

    visit_parser.add_argument(
            '--accounts',
            action=RepeatedOptionWithDefault,
            default=[pygs.DEFAULT_ACCOUNTS_FILE],
            dest='accounts_files',
            help=('The accounts file to use (default: {})'
                  ''.format(pygs.DEFAULT_ACCOUNTS_FILE)))

    # Use the extension defined above.
    parser.set_default_subparser('balance')
    parsed_args = vars(parser.parse_args())

    gpg_home = parsed_args.pop('gpg_home', None)
    config.CONFIG['gpg-home'] = gpg_home

    fn = parsed_args.pop('func')
    sys.exit(fn(**parsed_args))


def balance(accounts_files):
    # Q: Do we really need to support multiple configs at the same time?
    from . import gpgconfig
    from pathlib import Path
    import splinter
    browser = splinter.Browser(config.CONFIG.get('browser', 'chrome'))
    try:
        for accounts_file in accounts_files:
            accounts_file = Path(accounts_file)
            if not accounts_file.exists():
                raise ValueError("The accounts file doesn't exist. Perhaps you "
                                 "want to run the wizard?")
            accounts_config = gpgconfig.decrypt_config(accounts_file)
            for account in accounts_config.get('accounts', []):
                provider, credentials = core.Provider.from_config(account)
                provider.authenticate(browser, credentials)

                # for account_balance in provider.balances():
                #     print(account_balance.name, account_balance.total)
    finally:
        browser.quit()

def wizard(*args, **kwargs):
    from . import wizard as wizard_mod
    sys.exit(wizard_mod.wizard(*args, **kwargs))



def visit(accounts_files):
    # Q: Do we really need to support multiple configs at the same time?
    from . import gpgconfig
    from pathlib import Path
    import splinter
    browser = splinter.Browser(config.CONFIG.get('browser', 'chrome'))

    try:
        account_tabs = []
        for accounts_file in accounts_files:
            accounts_file = Path(accounts_file)
            if not accounts_file.exists():
                raise ValueError("The accounts file doesn't exist. Perhaps you "
                                 "want to run the wizard?")
            accounts_config = gpgconfig.decrypt_config(accounts_file)
            for account in accounts_config.get('accounts', []):
                provider, credentials = core.Provider.from_config(account)
                browser.execute_script('''window.open("about:blank", "_blank");''')
                window = browser.windows[-1]
                window.is_current = True
                steps = provider.authenticate(browser, credentials)
                account_tabs.append([window, steps])
                # for account_balance in provider.balances():
                #     print(account_balance.name, account_balance.total)
        while account_tabs:
            for window_and_steps in account_tabs[:]:
                window, steps = window_and_steps
                window.is_current = True
                try:
                    next(steps)
                except StopIteration:
                    account_tabs.remove(window_and_steps)

        while prompt_toolkit.prompt('Ready to close the browser? ').lower() in ['no', 'n']:
            pass
    finally:
        browser.quit()




if __name__ == '__main__':
    main()
