# python setup.py install

from setuptools import setup, find_packages

setup(
    name="offlinefoldersync",
    version="0.1.0",
    py_modules=["controllers", "main", "models", "views"],
    author="Sofiya Debois",
    install_requires=[
        "PyQt5",
        "matplotlib",
    ],
)
