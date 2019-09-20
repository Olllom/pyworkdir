"""
Command line interface
"""

from pyworkdir import WorkDir, forge_method

import textwrap
import inspect
import sys

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
    # collect commands
    for attribute in wd.custom_attributes:
        object = getattr(wd, attribute)
        if inspect.isfunction(object):
            main.command()(object)
    # default commands
    main.command()(forge_method(wd, show, replace_args={"workdir": wd}, add=False))
    return main


def entrypoint():
    """
    Entrypoint for the workdir command.
    """
    command_group = forge_command_line_interface()
    command_group()


# default command line interface functions
# ========================================


@click.option("-v", "--variables", count=True, help="Print custom variables.")
@click.option("-f", "--functions", count=True, help="Print custom functions.")
@click.option("-s", "--sources", count=True, help="Print source of custom attributes.")
@click.option("-e", "--environment", count=True, help="Print source of custom attributes.")
def show(workdir, variables=False, functions=False, sources=False, environment=False, out=sys.stdout):
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
    yaml.dump(dictionary, stream=out)
