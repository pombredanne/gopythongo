# -* encoding: utf-8 *-

import six

from semantic_version import Version as SemVerBase
from gopythongo.utils import highlight, print_error
from gopythongo.versioners.parsers import VersionContainer

versionparser_name = u"semver"


class SemVerVersion(SemVerBase):
    def __init__(self, *args):
        super(SemVerVersion, self).__init__(*args)

    def tostring(self):
        return six.u(self)


def add_args(parser):
    pass


def validate_args(parser):
    pass


def parse(version_str):
    try:
        sv = SemVerVersion.parse(version_str)
    except ValueError as e:
        print_error("%s is not a valid SemVer version string (%s)" % (highlight(version_str), str(e)))

    return VersionContainer(sv, versionparser_name)