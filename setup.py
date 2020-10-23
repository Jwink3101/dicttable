#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals, absolute_import

from setuptools import setup

with open('dicttable.py','rt') as file:
    for line in file:
        line = line.strip()
        if line.startswith('__version__'):
            __version__ = line.split('=',1)[1].strip()
            __version__ = eval(__version__) 
            break
    else:
        raise ValueError('Could not find __version__ in source')

from setuptools import setup

setup(
    name='dicttable',
    py_modules=['dicttable'],
    install_requires=[],
    long_description=open('readme.md').read(),
    entry_points = {},
    version=__version__,
    description='fast schemaless table object',
    url='https://github.com/Jwink3101/dicttable',
    author="Justin Winokur",
    author_email='Jwink3101@@users.noreply.github.com',
    license='MIT',
)
