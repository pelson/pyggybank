from .. import core


class TestProvider(core.Provider):
    names = ['Test provider']
    attributes = ['User ID (make it up)', 'password']
    domain = 'https://github.com/pelson/pyggybank/'
   
