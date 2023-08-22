#!/usr/bin/env python3
# Fred (W6BSD) 2022
#
import sys

from setuptools import setup

import sonde2kml

__author__ = "Fred C. (W6BSD)"
__version__ = sonde2kml.__version__
__license__ = 'BSD'

py_version = sys.version_info[:2]
if py_version < (3, 5):
  raise RuntimeError('sonde2kml requires Python 3.5 or later')

def readme():
  with open('README.md', encoding="utf-8") as fdr:
    return fdr.read()

setup(
  name='sonde2kml',
  version=__version__,
  description='Radiosondes KML files',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/0x9900/sonde2kml/',
  license=__license__,
  author=__author__,
  author_email='w6bsd@bsdworld.org',
  py_modules=['sonde2kml'],
  install_requires=['simplekml'],
  entry_points = {
    'console_scripts': ['sonde2kml = sonde2kml:main'],
  },
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Telecommunications Industry',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Topic :: Communications :: Ham Radio',
  ],
)
