#!/usr/bin/env python

"""
mixer
-----

mixer -- Description

"""

from os import path as op

from setuptools import setup

from mixer import __version__, __project__, __license__


def read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name=__project__,
    version=__version__,
    license=__license__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    platforms=('Any'),

    author='horneds',
    author_email='horneds@gmail.com',
    url='http://github.com/horneds/mixer',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    py_modules=['mixer'],
    install_requires=[
        l for l in read('requirements.txt').split('\n')
        if l and not l.startswith('#')],
    test_suite='tests',
    tests_require=[
        'django',
        'flask',
        'flask-sqlalchemy',
        'sqlalchemy',
    ]
)

# lint_ignore=F0401
