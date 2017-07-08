from distutils.core import setup
from distutils.version import StrictVersion
import sys


py_ver = StrictVersion('{v.major}.{v.minor}'.format(v=sys.version_info))
if py_ver < StrictVersion('3.6'):
    sys.exit('Sorry, Python < 3.6 is not supported.')


setup(
    name='pyggybank',
    description='Interface to your internet banking',
    version='0.1',
    author='Phil Elson',
    author_email='pelson.pub@gmail.com',
    url='https://github.com/pelson/pyggybank',
    license='BSD',
    packages=[
        'pyggybank', 'pyggybank.providers', 'pyggybank.gpgconfig'
    ],
    install_requires=['prompt_toolkit',
                      'splinter',
                      'ruamel.yaml',
                      'babel',
                      # The original python-gnupg, not to be confused with "gnupg"
                      # which installs to the same name.
                      'python-gnupg'],
    python_requires='>=3.6',
	entry_points={
          'console_scripts': [
              'pyggybank = pyggybank.cli:main'
          ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
)
