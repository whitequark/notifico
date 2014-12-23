#!/usr/bin/env python
# -*- coding: utf8 -*-
from setuptools import setup, find_packages


if __name__ == '__main__':
    setup(
        name='Notifico',
        version='0.1.0',
        author='Tyler Kennedy',
        author_email='tk@tkte.ch',
        entry_points={
            'console_scripts': [
                'notifico-cli = notifico.cli:from_cli'
            ]
        },
        packages=find_packages(),
        install_requires=[
            'Flask',
            'Flask-WTF==0.8.4',
            'Flask-Gravatar',
            'Flask-SQLAlchemy',
            'Flask-XML-RPC',
            'Flask-Mail',
            'Flask-Cache',
            'fabric',
            'sqlalchemy',
            'UtopiaIRC',
            'gevent',
            'oauth2',
            'redis',
            'gunicorn',
            'requests',
            'pygithub',
            'xmltodict',
            'unidecode',
            'raven',
            'blinker',
            'docopt',
            'celery'
        ],
        dependency_links=[
            'https://github.com/TkTech/utopia/tarball/deploy#egg=UtopiaIRC'
        ],
        include_package_data=True,
        zip_safe=False
    )
