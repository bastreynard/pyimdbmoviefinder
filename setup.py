from setuptools import setup, find_packages

setup(name='pymoviefinder', version='2.3', packages=find_packages(), entry_points={
        'console_scripts': ['pymoviefinder=pymoviefinder.cli.cli_search:main_cli'] # so this directly refers to a function available in __init__.py
        })