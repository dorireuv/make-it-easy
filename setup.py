#! /usr/bin/env python

# A tiny framework that makes it easy to write Test Data Builders in Python
# Port of Java make-it-easy by Nat Pryce
# Copyright (C) 2013 Dori Reuveni
# E-mail: dorireuv AT gmail DOT com


from setuptools import setup
import os
import re


__version__ = __author__ = __license__ = ''
fh = open(os.path.join(os.path.dirname(__file__), 'make_it_easy', '__init__.py'))
try:
    for line in fh:
        if re.match('^__[a-z_]+__.*', line):
            exec(line)
finally:
    if fh:
        fh.close()

params = dict(
    name='make-it-easy',
    version=__version__,
    packages=['make_it_easy'],
    author=__author__,
    author_email='dorireuv@gmail.com',
    description='A tiny framework that makes it easy to write Test Data Builders in Python',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    keywords=['testing', 'test', 'tdd', 'unittest', 'builder', 'goos'],
    url='https://www.github.com/dorireuv/make-it-easy',
    license=__license__,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
    ],
    tests_require=['PyHamcrest'],
    test_suite='tests',
)

setup(**params)