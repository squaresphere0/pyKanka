from setuptools import setup

install_requires = [
    "requests",
    "igraph"
]

setup(
    name = "pyKanka",
    install_requires = install_requires,
    version = '0.1',
    scripts = [],
    packages = ['pyKanka']
)
