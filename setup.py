#!/usr/bin/env python

""" mixer -- Generate tests data.

mixer -- Description

"""
from os import path as op

from setuptools import setup


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


install_requires = [
    d for d in _read('requirements.txt').split('\n')
    if d and not d.startswith('#')]


setup(
    packages=['mixer', 'mixer.backend'],
    include_package_data=True,
    install_requires=install_requires,
)

# lint_ignore=F0401
