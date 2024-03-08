from setuptools import setup, find_packages

setup(name='pyimdbmoviefinder', version='2.3', packages=find_packages(), entry_points={
        'console_scripts': ['pyimdbmoviefinder=pyimdbmoviefinder.cli.cli_search:main_cli'] # so this directly refers to a function available in __init__.py
        })