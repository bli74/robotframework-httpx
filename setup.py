#!/usr/bin/env python

import sys
from os.path import abspath, dirname, join

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PY3 = sys.version_info > (3,)

CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Topic :: Software Development :: Testing
"""[1:-1]

INSTALL_REQUIRE = ['robotframework>=3.2.2', 'httpx[http2]>=0.18.2', 'requests']
TEST_REQUIRE = ['pytest', 'flask', 'six', 'coverage', 'flake8', 'Werkzeug']
NTLM_REQUIRE = ['httpx_ntlm']

VERSION = None
version_file = join(dirname(abspath(__file__)), 'src', 'HttpxLibrary', 'version.py')
with open(version_file) as file:
    code = compile(file.read(), version_file, 'exec')
    exec(code)

DESCRIPTION = """
Robot Framework keyword library wrapper around the HTTP client library httpx.
"""[1:-1]

setup(name='robotframework-httpx',
      version=VERSION,
      description='Robot Framework keyword library wrapper around httpx',
      long_description=DESCRIPTION,
      author='Bulkan',
      author_email='bulkan@gmail.com',
      maintainer='Carl-Fredrik Sundstrom',
      maintainer_email='carl.f.sundstrom@gmail.com',
      url='https://github.com/',
      license='MIT',
      keywords='robotframework testing test automation http client httpx rest api',
      platforms='any',
      classifiers=CLASSIFIERS.splitlines(),
      package_dir={'': 'src'},
      packages=['HttpxLibrary'],
      install_requires=INSTALL_REQUIRE,
      extras_require={
          'ntlm': NTLM_REQUIRE,
          'test': TEST_REQUIRE
      })
