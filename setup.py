# coding: utf-8

"""Common Groups setup module."""

from setuptools import setup, find_packages

_about = {}
with open('commongroups/_about.py', 'r') as fp:
    exec(fp.read(), _about)

setup(
    name='commongroups',
    version=_about['__version__'],
    description=_about['desc'],
    long_description=_about['longdesc'],
    author=_about['__author__'],
    author_email=_about['__contact__'],
    url=_about['__url__'],
    license=_about['__license__'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Chemistry'
    ],
    keywords='science chemistry toxicology',
    packages=find_packages(),
    install_requires=[
        'ashes',
        'boltons',
        'gspread',
        'oauth2client',
        'pandas',
        'psycopg2',
        'sqlalchemy',
        'xlrd',
        'xlsxwriter'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['commongroups=commongroups.run:main']
    },
    include_package_data=True,
    package_data={
        '': ['tests/params.json', 'templates/*']
    },
    zip_safe=True
)
