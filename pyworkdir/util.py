"""
Utilities for workdir
"""


import functools
import inspect
import types


class WorkDirException(Exception):
    """
    General exception class for pyworkdir module.
    """
    pass


def add_method(instance, function, argument_to_replace_by_instance="self"):
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = (
        inspect.getfullargspec(function)
    )
    assert argument_to_replace_by_instance in args or argument_to_replace_by_instance in kwonlyargs
    if argument_to_replace_by_instance in args:
        args.remove(argument_to_replace_by_instance)
    def method(self, *fargs, **fkwargs):
        print(fargs, fkwargs)
        # turn arguments into keyword arguments
        for i, arg in enumerate(fargs):
            fkwargs[args[i]] = arg
        fkwargs[argument_to_replace_by_instance] = self
        print(fkwargs)
        return function(**fkwargs)
    setattr(instance, function.__name__, types.MethodType(method, instance))


