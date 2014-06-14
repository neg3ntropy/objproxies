#!/usr/bin/env python3

import setuptools
from os.path import join, dirname

setuptools.setup(
    name="objproxies",
    version="0.9.1",
    description="General purpose proxy and wrapper types",
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url="http://github.com/soulrebel/objproxies",
    author="Andrea Ratto",
    author_email="andrearatto_liste@yahoo.it",
    license="PSF or ZPL",
    test_suite='objproxies_tests',
    py_modules=['objproxies'],
    keywords='proxy pattern lazy wrapper',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
)
