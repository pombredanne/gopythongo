# -* encoding: utf-8 *-
import configargparse
import subprocess
import sys
import os

from typing import Dict, List, Tuple, Any

import gopythongo

from gopythongo.utils import print_info, highlight, create_script_path, print_warning, plugins, \
                             CommandLinePlugin, ErrorMessage
from gopythongo.utils.buildcontext import the_context
from gopythongo.builders import help as _builder_help

_builders = {}  # type: Dict[str, 'BaseBuilder']
_dependencies = {
    "debian/jessie": ["python", "python-pip", "python-dev", "python3-dev", "python-virtualenv",
                      "virtualenv", "binutils"]
}  # type: Dict[str, List[str]]


def get_dependencies() -> Dict[str, List[str]]:
    return _dependencies


def add_dependencies(key: str, deps: List[str]) -> None:
    global _dependencies
    _dependencies[key] = deps


def get_builders() -> Dict[str, 'BaseBuilder']:
    return _builders


def init_subsystem() -> None:
    global _builders

    from gopythongo.builders import docker, pbuilder, noisolation
    _builders = {
        "pbuilder": pbuilder.builder_class(),
        "docker": docker.builder_class(),
        "noisolation": noisolation.builder_class(),
    }

    plugins.load_plugins("gopythongo.builders", _builders, "builder_class", BaseBuilder, "builder_name")


class BaseBuilder(CommandLinePlugin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @property
    def builder_name(self) -> str:
        """
        **@property**
        """
        raise NotImplementedError("Each subclass of BaseBuilder MUST implement builder_name")

    def build(self, args: configargparse.Namespace) -> None:
        """
        Run a build environment while making sure that:
          * all folders listed in args.mounts and the_context.mounts are available inside the build environment
          * then run the command returned by the_context.get_gopythongo_inner_cmdline(args) inside the build
            environment
        :param args: the command-line arguments as parsed by GoPythonGo
        """
        raise NotImplementedError("Each subclass of BaseBuilder MUST implement build")

    def print_help(self) -> None:
        raise NotImplementedError("Each subclass of BaseBuilder MUST implement print_help")


def add_args(parser: configargparse.ArgumentParser) -> None:
    global _builders

    gr_builder = parser.add_argument_group("Common Builder options")
    gr_builder.add_argument("--mount", dest="mounts", action="append", default=[],
                            help="Additional folders to mount into the build environment. Due to limitations of "
                                 "the builders all paths will be mounted in place, i.e. in the same location where they "
                                 "exist on the host system.")
    gr_builder.add_argument("--builder-debug-login", dest="builder_debug_login", action="store_true",
                            default=False,
                            help="Instead of executing the '--inner' build, if the Builder supports it, run an "
                                 "interactive shell inside the build environment for debug purposes")
    gr_builder.add_argument("--run-after-create", dest="run_after_create", action="append",
                            help="Specify commands (e.g. shell scripts) which will be run using inside a build "
                                 "environment e.g. pbuilder or docker  after a build environment is created. This "
                                 "allows you to perform additional necessary build configuration, which shouldn't be "
                                 "repeated for each subsequent build (e.g. 'gem install fpm')")
    gr_builder.add_argument("--help-builder", choices=_builders.keys(), default=None,
                            action=_builder_help.BuilderHelpAction)

    for b in _builders.values():
        b.add_args(parser)


class NoMountableGoPythonGo(ErrorMessage):
    pass


def _test_gopythongo_version(cmd: List[str]) -> bool:
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).strip().decode("utf-8")
        if output == gopythongo.program_version:
            return True
        if len(output) >= 10 and output[:10] == gopythongo.program_version[:10]:
            raise NoMountableGoPythonGo("Mixed versions! %s is GoPthonGo, but a different version (%s vs. %s)" %
                                        (highlight(cmd[0]), highlight(output[11:]),
                                         highlight(gopythongo.program_version[11:])))
    except subprocess.CalledProcessError as e:
        raise NoMountableGoPythonGo("Error when trying to find out GoPythonGo version of nested executable. %s" %
                                    str(e)) from e

    raise NoMountableGoPythonGo("Found something, but it's not GoPythonGo? (%s)" % output)


def test_gopythongo(path: str) -> Tuple[str, List[str]]:
    """
    :returns: (str, list) -- A tuple containing the base path of the virtualenv/executable and a list containing
                             the executable and a list of command-line parameters necessary to execute GoPythonGo,
                             which can be passed to subprocess.Popen
    """
    if os.path.isfile(path):
        if os.access(path, os.X_OK):
            # path might be a PEX executable
            print_info("We found what is presumably a PEX executable in %s" % highlight(path))
            if _test_gopythongo_version([path, "--version"]):
                return os.path.dirname(path), [path]

    elif os.path.isdir(path):
        if os.access(create_script_path(path, "python"), os.X_OK):
            print_info("We found what is presumably a virtualenv in %s" % highlight(path))
            if _test_gopythongo_version([create_script_path(path, "python"), "-m", "gopythongo.main", "--version"]):
                return path, [create_script_path(path, "python"), "-m", "gopythongo.main"]
    raise NoMountableGoPythonGo("Can't find GoPythonGo as a virtualenv or PEX executable in %s" % path)


def validate_args(args: configargparse.Namespace) -> None:
    if args.builder:
        if args.builder in _builders.keys():
            _builders[args.builder].validate_args(args)

    for mount in args.mounts:
        if not os.path.exists(mount):
            raise ErrorMessage("Folder to be mounted does not exist: %s" % highlight(mount))

    gpg_path_found = False
    if os.getenv("VIRTUAL_ENV"):
        try:
            the_context.gopythongo_path, the_context.gopythongo_cmd = test_gopythongo(os.getenv("VIRTUAL_ENV"))
        except NoMountableGoPythonGo as e:
            print_warning("$VIRTUAL_ENV is set, but does not point to a virtual environment with GoPythonGo?")
        else:
            print_info("Propagating GoPythonGo to build environment from $VIRTUAL_ENV %s" %
                       (highlight(os.getenv("VIRTUAL_ENV"))))
            gpg_path_found = True
            the_context.mounts.add(the_context.gopythongo_path)

    if not gpg_path_found:
        test_path = os.path.dirname(os.path.dirname(sys.executable))

        try:
            the_context.gopythongo_path, the_context.gopythongo_cmd = test_gopythongo(test_path)
        except NoMountableGoPythonGo as e:
            raise ErrorMessage(str(e)) from e
        else:
            print_info("Propagating GoPythonGo to build environment from detected path %s" % (highlight(test_path)))
            the_context.mounts.add(the_context.gopythongo_path)
            gpg_path_found = True

    if not gpg_path_found:
        raise ErrorMessage("Can't detect GoPythonGo path. You should run GoPythonGo from a virtualenv.")

    if not args.is_inner:
        for ix, runspec in enumerate(args.run_after_create):
            if os.path.isfile(runspec):
                if not os.access(runspec, os.X_OK):
                    raise ErrorMessage("GoPythonGo is supposed to run %s inside the build environment, but it's not "
                                       "executable" % highlight(runspec))
                the_context.mounts.add(os.path.abspath(os.path.dirname(runspec)))
                if not os.path.isabs(runspec):
                    args.run_after_create[ix] = os.path.abspath(runspec)


def build(args: configargparse.Namespace) -> None:
    _builders[args.builder].build(args)
