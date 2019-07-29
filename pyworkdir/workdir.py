"""
workdir.py
Python working directories.
"""

import os
import pathlib
import importlib.util
import inspect
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
    settings (further down in the directory tree) override more general ones.

    When defining functions in the workdir.py file, some argument names have special meaning:
    - The argument name `workdir` refers to the working directory instance.
      It represents the `self` argument of the method.
    - The argument name `here` refers to the absolute path of the directory that contains the workdir.py file.

    """

    def __init__(self, directory=".", mkdir=True, python_files=["workdir.py"], yaml_files=["workdir.yaml"],
                 python_files_recursion=-1, yaml_files_recursion=-1):
        self.path = pathlib.Path(os.path.realpath(directory))
        self.scope_path = self.path
        self.custom_attributes = {}
        if mkdir:
            if self.path.is_file():
                raise WorkDirException(f"Workdir could not be created. {self.path} is a file.")
            elif not self.path.is_dir():
                os.mkdir(self.path)
        # read python files
        self.python_files = self._recursively_get_python_filenames(self.path, python_files, python_files_recursion)
        for pyfile in self.python_files:
            if (self.path/pyfile).is_file():
                self._initialize_from_pyfile(pyfile)

    def __enter__(self):
        self.scope_path = pathlib.Path.cwd()
        os.chdir(str(self.path))
        return self

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self.scope_path)
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

    def _initialize_from_pyfile(self, pyfile):
        """Initialize members of this WorkDir from a python file."""
        spec = importlib.util.spec_from_file_location("workdir_module", self.path/pyfile)
        pymod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pymod)
        for (name, object) in inspect.getmembers(pymod):
            if name.startswith("_") or inspect.ismodule(object):
                continue
            self.custom_attributes[name] = str(pyfile)
            object_wants_to_be_method = inspect.isfunction(object) and "workdir" in inspect.getfullargspec(object)[0]
            if object_wants_to_be_method:
                add_method(self, object, "workdir")
            else:
                setattr(self, name, object)

    @staticmethod
    def _recursively_get_python_filenames(path, python_files, python_files_recursion, current_recursion_level=0):
        this_dir_files = [path/pyfile for pyfile in python_files]
        if path.parent == path: # root directory
            return this_dir_files
        elif python_files_recursion == -1:
            parentfiles = WorkDir._recursively_get_python_filenames(
                path.parent, python_files, python_files_recursion, current_recursion_level+1)
            return parentfiles + this_dir_files
        elif current_recursion_level >= python_files_recursion:
            return this_dir_files
        else:
            parentfiles = WorkDir._recursively_get_python_filenames(
                path.parent, python_files, python_files_recursion, current_recursion_level+1)
            return parentfiles + this_dir_files


