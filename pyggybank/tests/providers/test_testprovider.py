import json
import urllib.parse
import uuid

from ... import core
from ... import exceptions


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
    domain = ('https://rawgit.com/pelson/pyggybank/master/pyggybank/tests/test_provider/'
              'start.html?{}'.format(urllib.parse.urlencode({'configJSON': json.dumps(config, separators=(',', ':'))}, quote_via=urllib.parse.quote)))

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


import pytest
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


def test_invalid_auth(browser):
    with pytest.raises(exceptions.AuthenticationError):
        p = auth_provider(browser, {'password': 'Not correct'})



def test_balances(browser):
    config = {'password': 'Basic password'}
    p = auth_provider(browser, config)
    bal = p.balances(browser)
    assert bal == {12}

