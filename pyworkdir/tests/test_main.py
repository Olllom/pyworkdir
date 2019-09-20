"""
Tests for command line interface
"""

from pyworkdir.main import forge_command_line_interface, entrypoint, show
from pyworkdir import WorkDir

import textwrap
from io import StringIO

import pytest
from click.testing import CliRunner
import yaml


def test_commandline_no_options(tmpdir):
    contents = textwrap.dedent(
        """
        import click
        
        def hi():
            print("hi")
        """
    )
    with open(tmpdir / "workdir.py", "w") as f:
        f.write(contents)
    main = forge_command_line_interface(directory=tmpdir)
    runner = CliRunner(env={"PWD":str(tmpdir)})
    result = runner.invoke(main, "hi")
    assert result.exit_code == 0
    assert result.output == "hi\n"


def test_commandline_options(tmpdir):
    contents = textwrap.dedent(
        """
        import click

        @click.option("-s")
        def hello(s):
            print("hello", s)
        """
    )
    with open(tmpdir / "workdir.py", "w") as f:
        f.write(contents)
    main = forge_command_line_interface(directory=tmpdir)
    runner = CliRunner(env={"PWD": str(tmpdir)})
    result = runner.invoke(main, ["hello", "-s", "friend"])
    print(result.output)
    assert result.exit_code == 0
    assert result.output == "hello friend\n"


def test_commandline_workdir_option(tmpdir):
    contents = textwrap.dedent(
        """
        import click

        @click.option("-s")
        @click.option("-p")
        def things(s, workdir, here, p):
            print(s)
            print(here/"here.tmp")
            print(workdir/"test.tmp")
            print(p)
        
        @click.option("-s")
        def hello(s):
            print("Hello", s)
        """
    )
    with open(tmpdir / "workdir.py", "w") as f:
        f.write(contents)
    main = forge_command_line_interface(directory=tmpdir)
    runner = CliRunner(env={"PWD": str(tmpdir)})
    result = runner.invoke(main, "--help")
    assert "things" in result.output
    assert "hello" in result.output
    result = runner.invoke(main, ["things", "-p", "thing2", "-s", "thing1"])
    print(result.output)
    wd = WorkDir(tmpdir)
    assert result.exit_code == 0
    assert result.output == '\n'.join(["thing1", str(wd/"here.tmp"), str(wd/"test.tmp"), "thing2", ""])


def test_imported_terminal_commands(tmpdir):
    """Test that a click-decorated functions show up even when they are imported."""
    content = textwrap.dedent(
        """
        from library import imported_function
        """)
    library = textwrap.dedent(
        """
        import click
        @click.option("-s")
        def imported_function(s):
            print(s)
        """)
    with open(tmpdir/"workdir.py", 'w') as f:
        f.write(content)
    with open(tmpdir/"library.py", 'w') as f:
        f.write(library)
    runner = CliRunner(env={"PWD": str(tmpdir)})
    main = forge_command_line_interface(directory=tmpdir)
    result = runner.invoke(main, "--help")
    assert "imported-function" in result.output


def test_entrypoint():
    with pytest.raises(SystemExit) as e:
        entrypoint()


def test_show(tmpdir):
    with WorkDir(tmpdir) as wd:
        out = StringIO()
        show(wd, True, True, True, True, out)
        dictionary = yaml.load(out.getvalue(), yaml.SafeLoader)
        attributes = set(dictionary["attributes"].keys())
        functions = set(dictionary["functions"])
        customs = attributes.union(functions)
        environment = set(dictionary["environment"])
        name = dictionary["name"]
        sources = dictionary["sources"]
        assert customs == set(wd.custom_attributes.keys())
        assert environment == set(wd.environment)
        assert name == str(tmpdir)
        assert sources == wd.custom_attributes
