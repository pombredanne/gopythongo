# -* encoding: utf-8 *-

from . import debianparser, help, regexparser, semverparser


class VersionContainer(object):
    def __init__(self, version, versiontype):
        self.version = version
        self.versiontype = versiontype
