"""
Command line interface
"""

from pyworkdir import WorkDir

import textwrap

import click


def forge_command_line_interface(*args, **kwargs):
    """Forge the click.Group that holds all commands defined in workdir.py"""
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
        if callable(object):
            main.command()(object)
    return main


def entrypoint():
    """Entrypoint for the workdir command. """
    command_group = forge_command_line_interface()
    command_group()
