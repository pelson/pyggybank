import pytest

from ..providers import testprovider
from .. import core


class Test_sanitise:
    schema = testprovider.TestProvider.schema()

    def test_not_dict(self):
        with pytest.raises(core.InvalidProviderConfig) as excinfo:
            assert self.schema.sanitise(None)
        excinfo.match(r"Config isn't dict-like.")

    def test_no_provider(self):
        with pytest.raises(core.InvalidProviderConfig) as excinfo:
            assert self.schema.sanitise({'a': '1'})
        excinfo.match(r'"provider" is missing from the config')

    def test_invalid_provider(self):
        with pytest.raises(core.InvalidProviderConfig) as excinfo:
            assert self.schema.sanitise({'provider': 'not what was needed'})
        excinfo.match(r'"not what was needed" is an invalid provider name')

    def test_missing_attributes(self):
        with pytest.raises(core.InvalidProviderConfig) as excinfo:
            assert self.schema.sanitise({'provider': 'Test provider'})
        assert 'No config item for "User ID (make it up)"' in str(excinfo.value)

    def test_too_many_attributes(self):
        with pytest.raises(core.InvalidProviderConfig) as excinfo:
            assert self.schema.sanitise({'provider': 'Test provider',
                                         'User ID (make it up)': 1234,
                                         'password': 'abc',
                                         'not allowed': 'woops'})
        assert ("The following config items are not allowed: not allowed"
                in str(excinfo.value))

    def test_goldilocks(self):
        assert self.schema.sanitise({'provider': 'Test provider',
                                     'User ID (make it up)': 1234,
                                     'password': 'abc'})

    def test_aliased_attribute(self):
        assert self.schema.sanitise({'provider': 'Test provider',
                                     'uid': 1234,
                                     'password': 'abc'})
