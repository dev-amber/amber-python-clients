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
    packages=['amber', 'amber.common', 'amber.dummy', 'amber.hokuyo', 'amber.ninedof', 'amber.roboclaw', 'amber.tests'],
    package_dir={'amber': 'src/amber',
                 'amber.common': 'src/amber/common',
                 'amber.dummy': 'src/amber/dummy',
                 'amber.hokuyo': 'src/amber/hokuyo',
                 'amber.ninedof': 'src/amber/ninedof',
                 'amber.roboclaw': 'src/amber/roboclaw',
                 'amber.tests': 'src/amber/tests'},
    package_data={'': ['src/amber/common/amber.ini',
                       'src/amber/dummy/dummy.ini',
                       'src/amber/hokuyo/hokuyo.ini',
                       'src/amber/ninedof/ninedof.ini',
                       'src/amber/roboclaw/roboclaw.ini']},
    data_files=[
        ('', [
            'src/amber/common/amber.ini',
            'src/amber/dummy/dummy.ini',
            'src/amber/hokuyo/hokuyo.ini',
            'src/amber/ninedof/ninedof.ini',
            'src/amber/roboclaw/roboclaw.ini',
        ]),
    ],
    include_package_data=True,
    install_requires=required,
    version='0.5',
    description='Amber clients in python',
    author=u'Paweł Suder',
    author_email='pawel@suder.info',
    url='http://project-capo.github.io/',
    download_url='http://github.com/project-capo/amber-python-clients/',
    keywords=['amber', 'hokuyo', 'roboclaw', 'ninedof', 'panda'],
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
