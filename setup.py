# -* encoding: utf-8 *-

from distutils.core import setup
from setuptools import find_packages

_package_root = "src/py"
_root_package = 'buildhelpers'

import time
_version = "1.0.dev%s" % int(time.time())
_packages = find_packages(_package_root, exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    name='net.maurus.buildhelpers',
    version=_version,
    packages=_packages,
    package_dir={
        '': _package_root,
    },
    install_requires=[
        'Jinja2',
        'ConfigArgParse'
    ],
)
