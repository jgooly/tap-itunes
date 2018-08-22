#!/usr/bin/env python

from setuptools import setup

setup(name='tap-itunes',
      version='0.0.1',
      description='Singer.io tap for extracting data from the iTunes Reporter.',
      author='Julian Ganguli',
      author_email='julianganguli+singer@gmail.com',
      url='https://github.com/jgooly/itunes-tap',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_itunes'],
      install_requires=[
          'singer-python==5.2.0',
          'requests==2.18.4',
          'pendulum==1.2.0',
          'python-dateutil==2.7.3'
      ],
      entry_points='''
          [console_scripts]
          tap-itunes=tap_itunes:main
      ''',
      packages=['tap_itunes'],
      package_data={
          'schemas': ['tap_itunes/schemas/*.json']
      },
      include_package_data=True,
      )
