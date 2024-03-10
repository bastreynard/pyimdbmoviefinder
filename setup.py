"""
Setup for python package
"""
from setuptools import setup, find_packages

setup(name='pyimdbmoviefinder', version='1.0', packages=find_packages(),
      install_requires=['requests', 'httplib2', 'cinemagoer',
                        'humanize', 'configparser', 'colorama'],
      entry_points={'console_scripts': [
          'pyimdbmoviefinder=pyimdbmoviefinder.clisearch:cli']}
      )
