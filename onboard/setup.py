from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'requirements.txt'), 'r') as req:
    requirements = [r for r in req.read().split("\n") if len(r) > 0]

setup(
    name='cycles.onboard',
    version='0.0.1',
    description='Onboard service for Raspberry Pi cycle computer',
    author='Ross Masters',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'onboard=cycles:main'
            ]
        }
    )
