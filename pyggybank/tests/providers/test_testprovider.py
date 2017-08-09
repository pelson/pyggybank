import json
import urllib.parse
import uuid

import pytest

from ... import core
from ... import exceptions
from ... import parse


def provider_url(config):
    qs = urllib.parse.urlencode(
            {'configJSON': json.dumps(config, separators=(',', ':'))},
            quote_via=urllib.parse.quote)
    return ('https://rawgit.com/pelson/pyggybank/master/pyggybank/tests/'
            'test_provider/start.html?{}'.format(qs))


class TestProvider(core.Provider):
    names = ['Test provider {}'.format(uuid.uuid4())]
    _attributes = ['password']
    config = {"accounts": {
                "page": "accounts_1"
              },
              "balance": {
                "page": "balances_1"
              },
              "auth": [
                {
                  "page": "login_1",
                  "pass": "Basic password"
                }
              ]
            }
    domain = provider_url(config)

    def authenticate(self, browser, credentials):
        self.log.info('Visiting {}'.format(self.domain))
        browser.visit(self.domain)
        self.log.info("Clicking Let's go")
        button = browser.find_by_xpath('''//input[contains(@value, "Let's g")]''')
        button.first.click()
        self.log.info("Inserting password")
        browser.find_by_xpath("//input[@name='pass']").first.fill(credentials.password)
        self.log.info("Clicking Login")
        button = browser.find_by_xpath('''//input[contains(@value, "Login")]''')
        button.first.click()

        self.log.info("Checking for sucessful authentication")
        # If the next page has a Login button, we clearly aren't authenticated.
        button = browser.find_by_xpath('''//input[contains(@value, "Login")]''')
        if button:
            raise exceptions.AuthenticationError()

    def balances(self, browser):
        self.log.info('Navigating to balances screen')
        balances = []
        accounts = list(browser.find_by_xpath("//tr"))[1:]
        for account in accounts:
            print(account.find_by_xpath('td'))
            id, name, acc_type, bal = [td.text for td in account.find_by_xpath('td')]
            bal = parse.parse_currency(bal, 'GBP')
            bal = {'id': id, 'name': name, 'amount': bal.float, 'currency': 'GBP', }
            balances.append(bal)
        return balances


@pytest.fixture(scope="module")
def browser():
    from splinter import Browser
    browser = Browser('chrome')
    yield browser
    browser.quit()



def auth_provider(browser, config):
    provider = TestProvider
    schema = provider.schema()
    config, credentials = schema.extract_credentials(config)
    p = provider.init_from_config(config)
    
#    try:
    p.authenticate(browser, credentials)
#    except Exception as err:
#        print(err)
#        import pdb; pdb.set_trace()
#        raise

    return p


@pytest.mark.BROWSER
def test_basic_auth(browser):
    config = {'password': 'Basic password'}
    p = auth_provider(browser, config)

    assert browser.is_text_present('This page is the simplest of balances in table form')


@pytest.mark.BROWSER
def test_invalid_auth(browser):
    with pytest.raises(exceptions.AuthenticationError):
        p = auth_provider(browser, {'password': 'Not correct'})


@pytest.mark.BROWSER
def test_balances(browser):
    config = {'password': 'Basic password'}
    p = auth_provider(browser, config)
    bal = p.balances(browser)
    expected = [{'amount': -124.86, 'currency': 'GBP', 'id': '1', 'name': 'My first account'},
                {'amount': -198765.43, 'currency': 'GBP', 'id': '2', 'name': 'My mortgage'},
                {'amount': 1234.56, 'currency': 'GBP', 'id': '3', 'name': 'My first saver'}]
    assert bal == expected

