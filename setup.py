from os.path import dirname, join

from setuptools import setup, find_packages

import pm4py


def read_file(filename):
    with open(join(dirname(__file__), filename)) as f:
        return f.read()


setup(
    name=pm4py.__name__,
    version=pm4py.__version__,
    description=pm4py.__doc__.strip(),
    long_description=read_file('README'),
    author=pm4py.__author__,
    author_email=pm4py.__author_email__,
    py_modules=[pm4py.__name__],
    include_package_data=True,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    url='http://www.pm4py.org',
    license='GPL 3.0',
    install_requires=[
        'pyvis',
        'networkx>=2.2',
        'matplotlib==2.2.2',
        'numpy',
        'ciso8601',
        'cvxopt',
        'lxml',
        'graphviz',
        'pandas==0.23.4',
        'scipy',
        'scikit-learn',
        'pulp'
    ],
    project_urls={
        'Documentation': 'http://pm4py.pads.rwth-aachen.de/documentation/',
        'Source': 'https://github.com/pm4py/pm4py-source',
        'Tracker': 'https://github.com/pm4py/pm4py-source/issues',
    }
)
