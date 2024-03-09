from setuptools import setup, find_packages

setup(name='pyimdbmoviefinder', version='1.0', packages=find_packages(), 
      install_requires=['requests', 'httplib2', 'cinemagoer', 'humanize', 'configparser'],
      entry_points={'console_scripts': ['pyimdbmoviefinder=pyimdbmoviefinder.cli.clisearch:cli']}
      )