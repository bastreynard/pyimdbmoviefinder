from setuptools import setup, find_packages

setup(name='pyimdbmoviefinder', version='1.0', packages=find_packages(), entry_points={
        'console_scripts': ['pyimdbmoviefinder=pyimdbmoviefinder.cli.clisearch:cli'] # so this directly refers to a function available in __init__.py
        })