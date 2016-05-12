# -* encoding: utf-8 *-
import argparse
from typing import List, Iterable


def init_color(no_color: bool): ...
def create_script_path(virtualenv_path: str, script_name: str) -> str: ...
def flatten(x: List) -> List: ...
def run_process(*args: Iterable[str]) -> None: ...
def print_error(message: str) -> None: ...
def print_warning(message: str) -> None: ...
def print_info(message: str) -> None: ...
def print_debug(message: str) -> None: ...
def success(message: str) -> None: ...
def highlight(message: str) -> str: ...


class GoPythonGoEnableSuper(object):
    def __init__(self, *args, **kwargs) -> None: ...


class CommandLinePlugin(GoPythonGoEnableSuper):
    def __init__(self, *args, **kwargs) -> None: ...

    def add_args(self, parser: argparse.ArgumentParser): ...
    def validate_args(self, args: argparse.Namespace): ...
