#!python3
# -*- coding: utf-8 -*-
"""
Reporting Pool

Copyright 2022 Anton Sobinov
https://github.com/nishbo/reporting_pool
"""

from setuptools import setup, find_packages

setup(
    name='reporting_pool',
    version='0.1.3',
    description='A wrapper around multiprocessing.Pool that keeps track of the completion.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/nishbo/reporting_pool',
    install_requires=[],
    author='Anton R Sobinov',
    author_email='an.sobinov@gmail.com',
    license='MIT',
    packages=find_packages())
