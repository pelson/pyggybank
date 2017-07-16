import pytest

from .. import pygs
from .. import core


class Test_load_provider_config_from_buffer:
    def test_dict_type(self):
        content = '[foobar]'

        with pytest.raises(TypeError) as excinfo:
            pygs.load_provider_config_from_buffer(content)
        excinfo.match(r'The config content should contain a dictionary at the top level, got .*list')

    def test_empty_content(self):
        content = '{}'

        with pytest.raises(ValueError) as excinfo:
            pygs.load_provider_config_from_buffer(content)
        excinfo.match(r'The accounts list was not defined in the config')

    def test_providers_not_a_list(self):
        content = '{accounts: {provider: Not real}}'

        with pytest.raises(ValueError) as excinfo:
            pygs.load_provider_config_from_buffer(content)
        excinfo.match(r'"accounts" config item should be a list of provider dictionaries')

    def test_fake_provider(self):
        content = '{accounts: [{provider: Not real}]}'

        with pytest.raises(ValueError) as excinfo:
            pygs.load_provider_config_from_buffer(content)
        excinfo.match(r'No provider found for "Not real"')

    def test_not_enough_credentials(self):
        # Note: testing of the Schema.sanitise is done elsewhere, we are just
        # testing it at a basic level.
        content = '{accounts: [{provider: Test provider}]}'

        with pytest.raises(core.InvalidProviderConfig) as excinfo:
            pygs.load_provider_config_from_buffer(content)
        excinfo.match('No config item for \"User ID \(make it up\)\"')
