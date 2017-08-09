from babel import numbers as n
cur_loc = 'en_US'
cur_loc = 'pt_BR'
test = [ (n.format_currency(123456.789, 'USD', locale=cur_loc), 'USD')
       , (n.format_currency(-123456.78, 'PLN', locale=cur_loc), 'PLN')
       , (n.format_currency(123456.789, 'PLN', locale=cur_loc), 'PLN')
       , (n.format_currency(123456.789, 'IDR', locale=cur_loc), 'IDR')
       , (n.format_currency(123456.789, 'JPY', locale=cur_loc), 'JPY')
       , (n.format_currency(-123456.78, 'JPY', locale=cur_loc), 'JPY')
       , (n.format_currency(123456.789, 'CNY', locale=cur_loc), 'CNY')
       , (n.format_currency(-123456.78, 'CNY', locale=cur_loc), 'CNY')
       ]

from .. import parse

for v,c in test:
    continue
    print('As currency :', c, ':', v.encode('utf-8'))
    info = parse.parse_currency(v, c)
    print('As value    :', c, ':', info.value)
    print('Extra info  :', info.name.encode('utf-8')
                         , info.symbol.encode('utf-8'))
