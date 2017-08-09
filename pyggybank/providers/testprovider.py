from .. import core


class TestProvider(core.Provider):
    names = ['Test provider']
    attributes = [core.attr('User ID (make it up)', alias='uid'),
                  'password']
    domain = 'https://cdn.rawgit.com/pelson/pyggybank/master/pyggybank/tests/test_provider/start.html?the-config-goes-here...'
