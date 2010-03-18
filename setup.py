#!/usr/bin/env python
import os
from setuptools import setup, find_packages

packages = find_packages()

setup(
    name='django-dependency',
    version='1.1',
    author='Caktus Consulting Group',
    author_email='solutions@caktusgroup.com',
    packages=find_packages(),
    scripts=['scripts/create_deps.py'],
    install_requires=['Django >= 1.1,==dev',],
    url='http://code.google.com/p/django-dependency/',
    license='LICENSE.txt',
    description='Django app to help manage external dependencies',
    long_description=open('README.txt').read(),
)
