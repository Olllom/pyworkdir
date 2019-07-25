"""
pyworkdir.py
Python working directories.
"""

import os
import traceback


class WorkDir(object):
    """
    Working directory class.

    Parameters
    ----------
    directory : str, Optional, default: "."
        The directory name

    Examples
    --------
    Basic usage:

    >>> with WorkDir():
    >>>     pass  # do something in the working directory
    """

    def __init__(self, directory="."):
        self.directory = directory

    def __enter__(self):
        self.old_path = os.getcwd()
        os.chdir(self.directory)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self.old_path)
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            return False
        return True



