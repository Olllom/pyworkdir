"""
Utilities for workdir
"""


import functools
import inspect
import types
from copy import copy


class WorkDirException(Exception):
    """
    General exception class for pyworkdir module.
    """
    pass


def add_method(instance, func, self_arg=None, replace_args=dict()):
    """
    Add a method to an object.

    Parameters
    ----------
    instance : class instance
        The instance to which the function should be added as a method
    func : function
        The function to be added to the instance
    self_arg : str or None, Optional, default = None
        The argument to be interpreted as self, representing the instance. The default is None, where
        the method behaves as a classmethod.
    replace_args : dict, Optional, default = dict()
        Any arguments that are replaced by default values in the spirit of functools.partial.
    """
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = (
        inspect.getfullargspec(func)
    )
    newargs = copy(args)
    for arg in replace_args:
        if arg in newargs:
            newargs.remove(arg)
    if self_arg is not None:
        if self_arg in newargs:
            newargs.remove(self_arg)

    @functools.wraps(func)
    def method(self, *fargs, **fkwargs):
        # turn arguments into keyword arguments
        for i, arg in enumerate(fargs):
            fkwargs[newargs[i]] = arg
        for arg in replace_args:
            if arg in args:
                fkwargs[arg] = replace_args[arg]
        print(self_arg)
        if self_arg is not None and self_arg in args:
            fkwargs[self_arg] = self
        return func(**fkwargs)

    setattr(instance, func.__name__, types.MethodType(method, instance))

