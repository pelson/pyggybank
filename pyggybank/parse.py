import re, os
from babel import numbers as n
from babel.core import default_locale


class AmountInfo(object):
    def __init__(self, name, symbol, value):
        self.name = name
        self.symbol = symbol
        self.value = value
        self.float = float(value)

    def __repr__(self):
        cur_loc = 'en_US'
        return n.format_currency(self.value, self.symbol, locale=cur_loc)


nasty_symbols = ['￡']

# https://stackoverflow.com/a/37598997/741316
def parse_currency(value, cur):
    decp = n.get_decimal_symbol()
    plus = n.get_plus_sign_symbol()
    minus = n.get_minus_sign_symbol()
    group = n.get_group_symbol()
    name = n.get_currency_name(cur)
    symbol = n.get_currency_symbol(cur)
    remove = [plus, name, symbol, group] + nasty_symbols
    for token in remove:
        # remove the pieces of information that shall be obvious
        value = re.sub(re.escape(token), '', value)
    # change the minus sign to a LOCALE=C minus
    value = re.sub(re.escape(minus), '-', value)
    # and change the decimal mark to a LOCALE=C decimal point
    value = re.sub(re.escape(decp), '.', value)
    # just in case remove extraneous spaces
    value = n.parse_decimal(re.sub('\s+', '', value))
    return AmountInfo(name, symbol, value)
