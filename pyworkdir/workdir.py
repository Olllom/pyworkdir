"""
pyworkdir.py
Python working directories.
"""

import os
import pathlib


class WorkDir(object):
    """
    Working directory class.

    Parameters
    ----------
    directory : str, Optional, default: "."
        The directory name

    Attributes
    ----------
    path: str
        Absolute path of this working directory

    old_path: str
        The path surrounding

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
    """

    def __init__(self, directory="."):
        self.path = pathlib.Path(os.path.realpath(directory))

    def __enter__(self):
        self.old_path = os.getcwd()
        os.chdir(str(self.path))
        return self

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self.old_path)
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
                yield os.path.join(self.path, element) if abs else element





