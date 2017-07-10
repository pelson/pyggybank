from .. import core


class TestProvider(core.Provider):
    names = ['Test provider']
    attributes = [core.attr('User ID (make it up)', alias='uid'),
                  'password']
    domain = 'https://github.com/pelson/pyggybank/'
