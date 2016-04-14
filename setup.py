# -* encoding: utf-8 *-

from distutils.core import setup
from setuptools import find_packages

_package_root = "src/py"
_root_package = 'gopythongo'

import time
_version = "1.0.dev%s" % int(time.time())
_packages = find_packages(_package_root, exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    name='gopythongo',
    version=_version,
    packages=_packages,
    package_dir={
        '': _package_root,
    },
    install_requires=[
        'Jinja2==2.8',
        'ConfigArgParse==0.9.3',
        'Sphinx==1.3.1',
        'sphinx-rtd-theme==0.1.9',
        'colorama==0.3.7',
    ],
)
