# coding=utf-8
# !/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    print 'No setuptools installed, use distutils'
    from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

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
        'amberclient.collision_avoidance',
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
        'amberclient.collision_avoidance': 'src/amberclient/collision_avoidance',
        'amberclient.examples': 'src/amberclient/examples'
    },
    package_data={'': [
        'src/amberclient/common/amber.ini',
        'src/amberclient/dummy/dummy.ini',
        'src/amberclient/hokuyo/hokuyo.ini',
        'src/amberclient/ninedof/ninedof.ini',
        'src/amberclient/roboclaw/roboclaw.ini',
        'src/amberclient/location/location.ini',
        'src/amberclient/drive_to_point/drive_to_point.ini',
        'src/amberclient/collision_avoidance/collision_avoidance.ini'
    ]},
    data_files=[
        ('', [
            'src/amberclient/common/amber.ini',
            'src/amberclient/dummy/dummy.ini',
            'src/amberclient/hokuyo/hokuyo.ini',
            'src/amberclient/ninedof/ninedof.ini',
            'src/amberclient/roboclaw/roboclaw.ini',
            'src/amberclient/location/location.ini',
            'src/amberclient/drive_to_point/drive_to_point.ini',
            'src/amberclient/collision_avoidance/collision_avoidance.ini'
        ]),
    ],
    test_suite="amberclient.tests",
    include_package_data=True,
    install_requires=required,
    version='0.14',
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
        'collision avoidance',
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
