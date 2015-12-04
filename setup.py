# coding=utf-8
# !/usr/bin/env python

import os

from setuptools.command.install import install as _install
from setuptools import setup

pwd = os.path.dirname(os.path.abspath(__file__))

with open('requirements.txt') as f:
    required = f.read().splitlines()
    required = [ req.split('#egg=')[1] if '#' in req else req for req in required ]


class Install(_install):
    def run(self):
        os.system('bash -x %s/protoc.sh' % pwd)
        _install.run(self)


setup(
    name='amber-python-clients',
    packages=[
        'amberclient',
        'amberclient.common',
        'amberclient.dummy',
        'amberclient.hokuyo',
        'amberclient.ninedof',
        'amberclient.roboclaw',
        'amberclient.location',
        'amberclient.drive_to_point',
        'amberclient.examples'
    ],
    package_dir={
        'amberclient': 'src/amberclient',
        'amberclient.common': 'src/amberclient/common',
        'amberclient.dummy': 'src/amberclient/dummy',
        'amberclient.hokuyo': 'src/amberclient/hokuyo',
        'amberclient.ninedof': 'src/amberclient/ninedof',
        'amberclient.roboclaw': 'src/amberclient/roboclaw',
        'amberclient.location': 'src/amberclient/location',
        'amberclient.drive_to_point': 'src/amberclient/drive_to_point',
        'amberclient.examples': 'src/amberclient/examples'
    },
    package_data={'': [
        'src/amberclient/common/amber.ini',
        'src/amberclient/dummy/dummy.ini',
        'src/amberclient/hokuyo/hokuyo.ini',
        'src/amberclient/ninedof/ninedof.ini',
        'src/amberclient/roboclaw/roboclaw.ini',
        'src/amberclient/location/location.ini',
        'src/amberclient/drive_to_point/drive_to_point.ini'
    ]},
    data_files=[
        ('', [
            'src/amberclient/common/amber.ini',
            'src/amberclient/dummy/dummy.ini',
            'src/amberclient/hokuyo/hokuyo.ini',
            'src/amberclient/ninedof/ninedof.ini',
            'src/amberclient/roboclaw/roboclaw.ini',
            'src/amberclient/location/location.ini',
            'src/amberclient/drive_to_point/drive_to_point.ini'
        ]),
    ],
    cmdclass={
        'install': Install
    },
    test_suite="amberclient.tests",
    include_package_data=True,
    install_requires=required,
    version='0.18',
    description='Amber clients in python',
    author=u'Paweł Suder',
    author_email='pawel@suder.info',
    url='http://project-capo.github.io/',
    download_url='http://github.com/project-capo/amber-python-clients/',
    keywords=[
        'amber',
        'dummy',
        'hokuyo',
        'ninedof',
        'roboclaw',
        'location',
        'drive to point',
        'panda'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    long_description='''\
'''
)
