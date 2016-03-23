#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='Pyjo-Reactor-Asyncio',
    version='0.0.1',
    description='Low level event reactor for Pyjoyment with asyncio support.',
    long_description=''.join(open('README.md').readlines()[2:]),
    author='Piotr Roszatycki',
    author_email='piotr.roszatycki@gmail.com',
    url='http://github.com/dex4er/Pyjo-Reactor-Asyncio',
    download_url='https://github.com/dex4er/Pyjo-Reactor-Asyncio/archive/master.zip',
    license='Artistic',
    include_package_data=True,
    zip_safe=True,
    keywords='mojo mojolicious pyjo pyjoyment reactor asyncio async',
    packages=find_packages(exclude=['t', 't.*']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Artistic License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Framework :: Pyjo',
    ],
    test_suite='test.TestSuite',
    extras_require={
       ':python_version < "3.0"': [
           'trollius',
       ],
    },
)
