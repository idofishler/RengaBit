#!/usr/bin/env python
from distutils.core import setup
from sys import version

trove = filter(bool, """
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: End Users/Desktop
Intended Audience :: Information Technology
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Communications :: File Sharing
Topic :: Software Development :: Libraries
Topic :: Utilities
""".splitlines())

if version < "2.2.3":
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

setup(
    name='pymktorrent',
    version='0.3',
    description='Torrent metadata (.torrent) creation utility and library',
    author='Ludvig Ericson',
    author_email='ludvig.ericson@gmail.com',
    url='http://labs.lericson.se/experiments/pymktorrent/',
    packages=['pymktorrent'],
    scripts=['pymktorrent/maketorrent.py'],
    classifiers=trove
)
