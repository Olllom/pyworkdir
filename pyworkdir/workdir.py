"""
workdir.py
Python working directories.
"""

import os
import pathlib
import importlib.util
import inspect
import logging
from copy import copy
from pyworkdir.util import WorkDirException, add_method


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
    yaml_files : list of string, Optional, default: ["workdir.yaml"]
        A list of configuration files to read a configuration from.
    python_files_recursion : int, Optional, default: -1
        Recursion level for loading python files from parent directories. 0 means only this directory, 1 means
        this directory and its parent directory, etc. If -1, recurse until root.
    yaml_files_recursion : int, Optional, default: -1
        Recursion level for yaml files.
    env : dict, Optional, default: dict()
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
    path: pathlib.Path
        Absolute path of this working directory
    scope_path: pathlib.Path
        The path of the surrounding scope (when used as a context manager)
    custom_attributes: dict
        A dictionary that lists custom attributes of this working directory. The values of the dictionary are
        the source files which contain the definition of each attribute.

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

    >>> with WorkDir(env={"VAR_ONE": "ONE", "VAR_TWO": "TWO"}):
    >>>     print(os.environ["VAR_ONE"])
    >>> assert "VAR_ONE" not in os.environ


    """
    def __init__(self, directory=".", mkdir=True, python_files=["workdir.py"], yaml_files=["workdir.yaml"],
                 python_files_recursion=-1, yaml_files_recursion=-1, env=dict(), logger=None, logfile="workdir.log",
                 loglevel_console=logging.INFO, loglevel_file=logging.DEBUG):
        # augment keyword arguments from yaml files
        #specified_args = locals()
        #args, _, _, defaults, _, _, _ = inspect.getfullargspec(self.__init__)
        #args.remove("self")
        #default_args = {kwarg: value for kwarg,value in zip(args, defaults)}
        #kwargs = _get_construction_kwargs(locals(), )
        self.path = pathlib.Path(os.path.realpath(directory))
        self.scope_path = copy(self.path)
        self.custom_attributes = {}
        if mkdir:
            if self.path.is_file():
                raise WorkDirException(f"Workdir could not be created. {self.path} is a file.")
            elif not self.path.is_dir():
                os.mkdir(self.path)
        # read yaml files
        self.yaml_files = self._recursively_get_filenames(self.path, yaml_files, yaml_files_recursion)
        for yaml_file in self.yaml_files:
            if (self.path/yaml_file).is_file():
                self._initialize_from_yaml_file(yaml_file)
        # read python files
        self.python_files = self._recursively_get_filenames(self.path, python_files, python_files_recursion)
        for pyfile in self.python_files:
            if (self.path/pyfile).is_file():
                self._initialize_from_pyfile(pyfile)
        # environment variables
        self.env = copy(env)
        self.scope_env = copy(env)
        # logging
        self.logger = logger
        self.logfile = logfile
        self.loglevel_console = loglevel_console
        self.loglevel_file = loglevel_file

    def __enter__(self):
        self.scope_path = pathlib.Path.cwd()
        os.chdir(str(self.path))
        if self.env:
            for variable in self.env:
                self.scope_env[variable] = os.environ.get(variable, None)
                os.environ[variable] = str(self.env[variable])
        return self

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self.scope_path)
        for variable in self.scope_env:
            pass
            if self.scope_env[variable] is None:
                pass
                del os.environ[variable]
            else:
                os.environ[variable] = self.scope_env[variable]
        if exc_type is not None:
            # do logging here traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True

    def __str__(self):
        return str(self.path)

    def __truediv__(self, other):
        return self.path / other

    def __len__(self):
        return len(os.listdir(str(self.path)))

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

    def _initialize_from_pyfile(self, pyfile):
        """Initialize members of this WorkDir from a python file."""
        spec = importlib.util.spec_from_file_location("workdir_module", self.path/pyfile)
        pymod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pymod)
        for (name, object) in inspect.getmembers(pymod):
            if name.startswith("_") or inspect.ismodule(object):
                continue
            self.custom_attributes[name] = str(pyfile)
            if inspect.isfunction(object):
                add_method(self, object, self_arg="workdir",
                           replace_args={"here": pathlib.Path(os.path.dirname(pyfile))})
            else:
                setattr(self, name, object)

    @staticmethod
    def _recursively_get_filenames(path, filenames, recursion_depth, current_recursion_level=0):
        """Get all filenames (python/yaml) that attributes should be read from."""
        this_dir_files = [path / pyfile for pyfile in filenames]
        if path.parent == path: # root directory
            return this_dir_files
        elif recursion_depth == -1:
            parentfiles = WorkDir._recursively_get_filenames(
                path.parent, filenames, recursion_depth, current_recursion_level + 1)
            return parentfiles + this_dir_files
        elif current_recursion_level >= recursion_depth:
            return this_dir_files
        else:
            parentfiles = WorkDir._recursively_get_filenames(
                path.parent, filenames, recursion_depth, current_recursion_level + 1)
            return parentfiles + this_dir_files

    def _initialize_from_yaml_file(self, yaml_file):
        pass

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
