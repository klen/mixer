#!/usr/bin/env python

"""
mixer
-----

mixer -- Description

"""

import sys
from os import path as op

from setuptools import setup

from mixer import __version__, __project__, __license__


def read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

tests_require = [
    'django',
    'flask-sqlalchemy',
    'sqlalchemy',
    'mongoengine',
]
install_requires = [l for l in read('requirements.txt').split('\n')
                    if l and not l.startswith('#')]

if sys.version_info < (2, 7):
    install_requires.append('importlib')

elif sys.version_info > (3, 0):
    tests_require.remove('flask-sqlalchemy')


setup(
    name=__project__,
    version=__version__,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),
    keywords = "django flask sqlalchemy testing mock stub mongoengine".split(),

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    url='http://github.com/klen/mixer',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],

    packages=['mixer', 'mixer.backend'],
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
)

# lint_ignore=F0401
