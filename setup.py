#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = ["chess"]

setup(
    name="heckmeckengine",
    version="0.0.1",
    author="Max Mihailescu",
    packages=find_packages(),
    install_requires=install_requires,
)
