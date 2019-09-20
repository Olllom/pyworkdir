"""
Python working directories.
"""

import os
import pathlib
import inspect
import logging
import traceback
from copy import copy
from pyworkdir.util import (
    WorkDirException, forge_method, recursively_get_filenames, import_from_file)

import yaml
import jinja2


class WorkDir(object):
    """
    Working directory class.

    Parameters
    ----------
    directory : str, Optional, default: "."
        The directory name
    mkdir : bool, Optional, default: True
        Whether to create the directory if it does not exist
    python_files : list of string, Optional, default: ["workdir.py"]
        A list of python files. All variables, functions, and classes defined
        in these files are added as members to customize the WorkDir.
    yml_files : list of string, Optional, default: ["workdir.yml"]
        A list of configuration files to read a configuration from.
    python_files_recursion : int, Optional, default: -1
        Recursion level for loading python files from parent directories. 0 means only this directory, 1 means
        this directory and its parent directory, etc. If -1, recurse until root.
    yml_files_recursion : int, Optional, default: -1
        Recursion level for yml files.
    environment : dict, Optional, default: dict()
        A dictionary. Keys (names of environment variables) and values (values of environment variables)
        have to be strings. Environment variables are temporarily set to these values within a context
        (a `with WorkDir() ...` block) and set to their original values outside the context.
    logger : logging.Logger or None, Optional, default: None
        A logger instance. If None, use a default logger. If a custom logger is specified,
        the other arguments that concern the logger are not recognized.
    logfile : str, Optional, default: "workdir.log"
        The logfile to write output to.
    loglevel_console : int, Optional, default: logging.INFO
        The level of logging to the console.
    loglevel_file : int, Optional, default: logging.DEBUG
        The level of logging to the logfile.

    Attributes
    ----------
    path : pathlib.Path
        Absolute path of this working directory
    scope_path : pathlib.Path
        The path of the surrounding scope (when used as a context manager)
    environment : dict
        A dictionary of environment variables to be set in the context
    scope_environment : dict
        A dictionary to keep track of the environment of the scope
    custom_attributes : dict
        A dictionary that lists custom attributes of this working directory. The values of the dictionary are
        the source files which contain the definition of each attribute.
    python_files : list of str
        A list of python filenames that the workdir instance may read its custom attributes from.
        Files do not need to exist.
    yml_files: list of str
        A list of yml filenames that the workdir instance may read its custom attributes from.
        Files do not need to exist.
    logger : logging.Logger or None
        A logger instance
    logfile : str
        Filename of the log file
    loglevel_console : int
        An integer between 0 (logging.NOT_SET) and 50 (logging.CRITICAL) for level of printing to the console
    loglevel_file : int
        An integer between 0 (logging.NOT_SET) and 50 (logging.CRITICAL) for level of printing to the file


    Notes
    -----
    Get the absolute path of a file in this working directory

    >>> with WorkDir("some_path") as wd:
    >>>     absolute_path = wd / "some_file.txt"

    Get the number of files and subdirectories:

    >>>     len(wd)

    Iterate over all files in this working directory:

    >>>     for f in wd.files():
    >>>         pass

    Examples
    --------
    Basic usage:

    >>> with WorkDir("some_path"):
    >>>     # everything in this context will
    >>>     # run in the specified directory
    >>>     pass

    Customizing the working directory:

    To add or change attributes of the WorkDir, create a file "workdir.py" in the directory.
    All functions, classes, and variables defined in "workdir.py" will be added as attributes to the WorkDir.

    >>> # -- workdir.py --
    >>> def custom_sum_function(a, b):
    >>>     return a + b

    >>> # -- main.py --
    >>> wd = WorkDir(".")
    >>> result = wd.custom_sum_function(a,b)

    By default, these attributes get added recursively from parent directories as well, where more specific
    settings (further down in the directory tree) override more general ones. This mimics a kind of inheritance,
    where subdirectories inherit attributes from their parents.

    When defining functions in the workdir.py file, some argument names have special meaning:
    - The argument name `workdir` refers to the working directory instance.
      It represents the `self` argument of the method.
    - The argument name `here` refers to the absolute path of the directory that contains the workdir.py file.

    Environment variables can be changed inside a context as follows.

    >>> import os
    >>> with WorkDir(environment={"VAR_ONE": "ONE", "VAR_TWO": "TWO"}):
    >>>     print(os.environ["VAR_ONE"])
    >>> assert "VAR_ONE" not in os.environ

    Environment variables and simple attributes can also be set through yml files.
    The templates `{{ workdir }}` and `{{ here }}` are available and will be replaced by the working directory
    instance and the directory that contains the yml file, respectively.

    >>> # -- workdir.yml --
        environment:
            VAR_ONE: "a"
        attributes:
            my_number: 1
            my_list:
                - 1
                - 2
                - 3
            my_tmpdir: {{ here/"tmpdir" }}
            my_local_tmpfile: {{ workdir/"file.tmp" }}

    >>> with WorkDir() as wd:
    >>>     print(wd.my_number + 5, wd.my_tmpdir , wd.my_local_tmpfile)
    >>>     for el in wd.my_list:
    >>>          print(el)
    >>>     print(os.environ["VAR_ONE"])

    Note that environment variables passed to the constructor have preference over those in a yml file.

    A logging instance is available; the default output file is workdir.log:

    >>> wd = WorkDir()
    >>> wd.log("my message")
    >>> import logging
    >>> wd.log("debug info", level=logging.DEBUG)


    """
    def __init__(
            self,
            directory=".",
            mkdir=True,
            python_files=["workdir.py"],
            yml_files=["workdir.yml"],
            python_files_recursion=-1,
            yml_files_recursion=-1,
            environment=dict(),
            logger=None,
            logfile="workdir.log",
            loglevel_console=logging.INFO,
            loglevel_file=logging.DEBUG
    ):
        self.path = pathlib.Path(os.path.realpath(directory))
        self.scope_path = copy(self.path)
        self.custom_attributes = {}
        if mkdir:
            if self.path.is_file():
                raise WorkDirException(f"Workdir could not be created. {self.path} is a file.")
            elif not self.path.is_dir():
                os.mkdir(self.path)
        # read python files
        self.python_files = recursively_get_filenames(self.path, python_files, python_files_recursion)
        for pyfile in self.python_files:
            if (self.path/pyfile).is_file():
                self.add_members_from_pyfile(pyfile)
        # logging
        self.logger = logger
        self.logfile = logfile
        self.loglevel_console = loglevel_console
        self.loglevel_file = loglevel_file
        # environment variables
        self.environment = dict()
        # read yml files
        self.yml_files = recursively_get_filenames(self.path, yml_files, yml_files_recursion)
        for yml_file in self.yml_files:
            if (self.path/yml_file).is_file():
                self.add_members_from_yml_file(self.path / yml_file)
        self.environment.update(environment)
        self.scope_environment = copy(self.environment)

    def __enter__(self):
        self.scope_path = pathlib.Path.cwd()
        os.chdir(str(self.path))
        if self.environment:
            for variable in self.environment:
                self.scope_environment[variable] = os.environ.get(variable, None)
                os.environ[variable] = str(self.environment[variable])
        return self

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self.scope_path)
        for variable in self.scope_environment:
            if self.scope_environment[variable] is None:
                del os.environ[variable]
            else:
                os.environ[variable] = self.scope_environment[variable]
        if exc_type is not None:
            if self.logger is not None:
                self.log(traceback.format_exc(), level=logging.ERROR)
            return False
        return True

    def __str__(self):
        return str(self.path)

    def __truediv__(self, other):
        return self.path / other

    def __len__(self):
        return len(os.listdir(str(self.path)))

    #def __call__(self, *command, **kwargs):
    #    self.terminal_command(command, **kwargs)

    #def terminal_command(self, command, decoding="latin-1"):
    #    if len(command) == 1 and isinstance(command[0], str):
    #        command = [shlex.split(command)]
    #    assert len(command) > 0
    #    p = subprocess.Popen(command, stdout=subprocess.PIPE)
    #    out, err = p.communicate()
    #    return out.decode(decoding)[:-1]

    def files(self, abs=False):
        """
        Iterator over files in this work dir.

        Parameters
        ----------
        abs : bool, Optional, default=False
            Yield absolute filenames

        Yields
        ------
        file : str
            Filenames in this directory

        Examples
        --------
        >>> with WorkDir("some_directory") as wd:
        >>>     for file in wd.files():
        >>>         print(file)
        """
        for element in os.listdir(str(self.path)):
            if os.path.isfile(element):
                yield self.path/element if abs else pathlib.Path(element)

    def log(self, message, level=logging.INFO):
        """
        Write logging output to the console and/or a log file.

        Parameters
        ----------
        message : str
        level : int, Optional, default: logging.DEBUG
        """
        if self.logger is None:
            self._create_logger()
        self.logger.log(level, message)

    def add_members_from_pyfile(self, pyfile):
        """
        Initialize members of this WorkDir from a python file.

        The following attributes are not added as members of the WorkDir:

        1) imported modules
        2) built-ins and private objects, i.e. if the name starts with an underscore
        3) objects that are imported from other modules using `from ... import ...`

        The only exception to 3. is if the imported function has a command-line interface,
        i.e. `@click.option`-decorated functions added to the workdir so that they can be
        called from the command line.

        Parameters
        ----------
        pyfile : path-like object
            Absolute path of a python file.

        Notes
        -----
        The function arguments `workdir` and `here` of imported functions
        are replaced by the WorkDir instance and the directory containing the
        pyfile, respectively.
        """
        pymod = import_from_file(pyfile)

        for (name, object) in inspect.getmembers(pymod):
            # skip all imports
            if inspect.ismodule(object):
                continue
            # skip all built-ins and private objects
            if name.startswith("_"):
                continue
            # skip all objects that are not defined in this module (if they are not command-line callables)
            if (
                    hasattr(object, "__module__")
                    and object.__module__ != "pyfile_module"
                    and not hasattr(object, "__click_params__")
            ):
                continue
            self.custom_attributes[name] = str(pyfile)
            if inspect.isfunction(object):
                forge_method(
                    self,
                    object,
                    replace_args={"workdir": self, "here": pathlib.Path(os.path.dirname(pyfile))},
                    name=name
                )
            else:
                setattr(self, name, object)

    def add_members_from_yml_file(self, yml_file):
        """
        Initialize members and environment variables from a yml file.
        """
        with open(yml_file, "r") as f:
            dictionary = yaml.load(jinja2.Template(f.read()).render(workdir=self, here=yml_file.parent), Loader=yaml.SafeLoader)
            if "attributes" in dictionary:
                for attribute in dictionary["attributes"]:
                    self.custom_attributes[attribute] = str(yml_file)
                    setattr(self, attribute, dictionary["attributes"][attribute])
            if "environment" in dictionary:
                self.environment.update(dictionary["environment"])

    def _create_logger(self):
        """Create a default logger."""
        assert self.logger is None
        # create logger instance
        self.logger = logging.getLogger('{}'.format(self.path))
        self.logger.setLevel(logging.DEBUG)
        # File logging
        log_file = self.path/self.logfile
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.loglevel_file)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.loglevel_console)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

