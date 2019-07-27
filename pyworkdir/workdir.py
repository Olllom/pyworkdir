"""
pyworkdir.py
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
    mkdir: bool, Optional, default: True
        Whether to create the directory if it does not exist

    Attributes
    ----------
    path: pathlib.Path
        Absolute path of this working directory
    scope_path: pathlib.Path
        The path of the surrounding scope (when used as a context manager)

    Notes
    -----
    Get the absolute path of a file in this working directory

    >>> with WorkDir("some_path") as wd:
    >>>     absolute_path = wd / "some_file.txt"

    Get the number of files and subdirectories:

    >>>     len(wd)

    Examples
    --------
    Basic usage:

    >>> with WorkDir("some_path"):
    >>>     # everything in this context will
    >>>     # run in the specified directory
    >>>     pass

    Extending the functionality:

    ```
    def custom_function(filename, workdir, a, b):
        pass
    ```


    >>>

    """

    def __init__(self, directory=".", mkdir=True, yaml_files=["workdir.yaml"], python_files=["workdir.py"],
                 recursive_load_yaml=True, recursive_load_py=True):
        self.path = pathlib.Path(os.path.realpath(directory))
        self.scope_path = self.path
        if mkdir:
            if self.path.is_file():
                raise WorkDirException(f"Workdir could not be created. {self.path} is a file.")
            elif not self.path.is_dir():
                os.mkdir(self.path)
        self.logger = None
        self.python_files = python_files
        for pyfile in python_files:
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
            object_wants_to_be_method = inspect.isfunction(object) and "workdir" in inspect.getfullargspec(object)[0]
            if not name.startswith("_") and not inspect.ismodule(object):
                if object_wants_to_be_method:
                    print(inspect.getfullargspec(object))
                    add_method(self, object, "workdir")
                else:
                    setattr(self, name, object)



