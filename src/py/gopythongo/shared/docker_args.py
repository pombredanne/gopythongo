# -* encoding: utf-8 *-
import os
import argparse

from gopythongo.utils import highlight, ErrorMessage

_docker_shared_args_added = False  # type: bool


def add_shared_args(parser: argparse.ArgumentParser) -> None:
    global _docker_shared_args_added

    if not _docker_shared_args_added:
        gr_docker_shared = parser.add_argument_group("Docker common parameters")
        gr_docker_shared.add_argument("--use-docker", dest="docker_executable", default="/usr/bin/docker",
                                      help="Specify an alternative docker executable.")

    _docker_shared_args_added = True


def validate_shared_args(args: argparse.Namespace) -> None:
    if not os.path.exists(args.docker_executable) or not os.access(args.docker_executable, os.X_OK):
        raise ErrorMessage("docker not found in path or not executable (%s). You can specify "
                           "an alternative path using %s" %
                           (args.docker_executable, highlight("--use-docker")))
