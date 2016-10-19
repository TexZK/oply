try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    with open('README.md') as f:
        return f.read()


config = {
    'name': 'oply',
    'description': 'Yamaha OPL emulation',
    'long_description': readme(),

    'url': 'http://github.com/TexZK/oply',

    'version': '0.0.1',
    'author': 'Andrea Zoppi',
    'author_email': 'texzk@email.it',
    'license': 'GPL3',

    'packages': ['oply'],
    'install_requires': [],
    'keywords': 'yamaha opl adlib imf',

    'test_suite': 'nose.collector',
    'tests_require': ['nose'],

    'include_package_data': True,
    'zip_safe': False,
}

setup(**config)
