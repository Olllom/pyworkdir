"""
Utilities for workdir
"""

import os
import sys
import importlib
import functools
import inspect
import click
from copy import copy


class WorkDirException(Exception):
    """
    General exception class for pyworkdir module.
    """
    pass


def recursively_get_filenames(path, filenames, recursion_depth, current_recursion_level=0):
    """
    Get all filenames (python/yaml) that attributes should be read from.

    Parameters
    ----------
    path : str or path-like object
        the current directory
    filenames : str
        The base filenames.
    recursion_depth : int
        The maximum recursion depth (0 = only current directory, 1 = current and parents).
        -1 means recurse until root.
    current_recursion_level : int, Optional, default = 0
        Current recursion level of the function.

    Returns
    -------
    filenames: list
        A list of filenames, where the ones further up front in the list are further up in the directory tree.
        The files do not need to exist.
    """
    this_dir_files = [path / pyfile for pyfile in filenames]
    if path.parent == path: # root directory
        return this_dir_files
    elif recursion_depth == -1:
        parentfiles = recursively_get_filenames(
            path.parent, filenames, recursion_depth, current_recursion_level + 1)
        return parentfiles + this_dir_files
    elif current_recursion_level >= recursion_depth:
        return this_dir_files
    else:
        parentfiles = recursively_get_filenames(
            path.parent, filenames, recursion_depth, current_recursion_level + 1)
        return parentfiles + this_dir_files


def add_function(instance, func, replace_args=dict(), name=None):
    """
    Add a function to an object.

    Parameters
    ----------
    instance : class instance
        The instance to which the function should be added as a method
    func : function
        The function to be added to the instance
    replace_args : dict, Optional, default = dict()
        Any arguments that are replaced by default values in the spirit of functools.partial
    name : str, Optional, default=None
        The function's name; if None, infer from function.__name__

    Notes
    -----
    This function takes care of option-decorated functions. They retain
    their __click_params__ field; also all `replace_args`
    get added as hidden options so that they are not visible on the command line interface.
    """
    if name is None:
        name = func.__name__
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = (
        inspect.getfullargspec(func)
    )
    newargs = copy(args)
    for arg in replace_args:
        if arg in newargs:
            newargs.remove(arg)

    @functools.wraps(func)
    def method(*fargs, **fkwargs):
        # turn arguments into keyword arguments
        for i, arg in enumerate(fargs):
            fkwargs[newargs[i]] = arg
        for arg in replace_args:
            if arg in args:
                fkwargs[arg] = replace_args[arg]
        return func(**fkwargs)

    # enable replace_args for click command-line interface
    for arg in replace_args:
        if arg in args:
            method = click.option(
                "--{}".format(arg.replace("_","-").replace(" ","-")),
                default=replace_args[arg],
                hidden=True
            )(method)

    setattr(instance, name, method)


def import_from_file(filename):
    """
    Import a python module from a file by path.

    Parameters
    ----------
    filename : str or path-like
        The file to be imported

    Returns
    -------
    pymod : python module
        The imported module
    """
    # include the path in the pythonpath to resolve local imports
    old_modules = copy(sys.modules)
    sys.path.insert(0, os.path.realpath(os.path.dirname(filename)))  # to resolve local import in pyfile

    # load module
    loader = importlib.machinery.SourceFileLoader("pyfile_module", str(filename))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    pymod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pymod)

    # reset sys.path and sys.modules to allow importing other modules with the same name
    sys.path.pop(0)
    sys.modules = old_modules

    return pymod
