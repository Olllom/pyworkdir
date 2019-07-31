"""
Tests for command line interface
"""

from pyworkdir.main import forge_command_line_interface, entrypoint
from pyworkdir import WorkDir

import textwrap

from click.testing import CliRunner


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
        """
    )
    with open(tmpdir / "workdir.py", "w") as f:
        f.write(contents)
    main = forge_command_line_interface(directory=tmpdir)
    runner = CliRunner(env={"PWD": str(tmpdir)})
    result = runner.invoke(main, ["things", "-p", "thing2", "-s", "thing1"])
    print(result.output)
    wd = WorkDir(tmpdir)
    assert result.exit_code == 0
    assert result.output == '\n'.join(["thing1", str(wd/"here.tmp"), str(wd/"test.tmp"), "thing2", ""])
