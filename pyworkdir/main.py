"""
Command line interface
"""

import pyworkdir
from pyworkdir import WorkDir, forge_method

import textwrap
import inspect
import sys
import os

import yaml
import click


def forge_command_line_interface(*args, **kwargs):
    """
    Forge the click.Group that holds all commands defined in workdir.py
    All arguments are forwarded to the constructor of WorkDir.

    Returns
    -------
    A click.Group that defines one command for every custom function in the WorkDir.
    """
    wd = WorkDir(*args, **kwargs)
    main = click.Group(
        name="workdir",
        help=textwrap.dedent(
            """
            Commands in this working directory.
            Add commands by defining functions in workdir.py;
            decorate them with "@click.option(...)" to define function parameters as command line options.
            """)
    )
    # add version option
    main = click.version_option(version=pyworkdir.__version__, prog_name="pyworkdir")(main)
    # collect commands
    for attribute in wd.custom_attributes:
        object = getattr(wd, attribute)
        if inspect.isfunction(object) and not hasattr(object, "__nocli__"):
            main.command()(object)
    for command in wd.commands:
        bash, doc = wd.commands[command].split("//")
        cmd = click.Command(command, callback=bash_function(bash), help=doc)
        main.add_command(cmd)
    # default commands
    main.command()(forge_method(wd, show, replace_args={"workdir": wd}, add=False))
    return main


def entrypoint():
    """
    Entrypoint for the workdir command.
    """
    command_group = forge_command_line_interface()
    command_group()


def no_cli(function):
    """Function decorator to suppress generation of a command-line interface for this function.

    Examples
    --------
    >>> # in workdir.py
    >>> from pyworkdir import no_cli
    >>>
    >>> @no_cli
    >>> def function_without_command_line_interace()
    >>>     pass
    """
    setattr(function, "__nocli__", True)
    return function


def bash_function(bash_command):
    """Bash command as a python function

    Parameters
    ----------
    bash_command : str

    Returns
    -------
    function : callable
        A python function that runs the bash command.
    """

    return lambda: os.system(bash_command)


# default command line interface functions
# ========================================


@click.option("-v", "--variables", count=True, help="Print custom variables.")
@click.option("-f", "--functions", count=True, help="Print custom functions.")
@click.option("-s", "--sources", count=True, help="Print source of custom attributes.")
@click.option("-e", "--environment", count=True, help="Print source of custom attributes.")
@click.option("-c", "--commands", count=True, help="Print source of terminal commands.")
def show(workdir, variables=False, functions=False, sources=False, environment=False, commands=False, out=sys.stdout):
    """Print the working directory in yaml format."""
    dictionary = {"name": str(workdir)}
    if variables:
        variables = dict()
        for attribute in workdir.custom_attributes:
            if not callable(getattr(workdir, attribute)):
                variables[attribute] = getattr(workdir, attribute)
        dictionary["attributes"] = variables
    if functions:
        functions = []
        for attribute in workdir.custom_attributes:
            if callable(getattr(workdir, attribute)):
                functions.append(attribute)
        dictionary["functions"] = functions
    if sources:
        dictionary["sources"] = workdir.custom_attributes
    if environment:
        dictionary["environment"] = workdir.environment
    if commands:
        dictionary["commands"] = workdir.commands
    yaml.dump(dictionary, stream=out)


