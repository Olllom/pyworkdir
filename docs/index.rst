.. pyworkdir documentation master file, created by
   sphinx-quickstart on Thu Mar 15 13:55:56 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pyworkdir's documentation!
=========================================================

Visit `project home on GitHub.`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:


.. _`project home on GitHub.`: https://github.com/Olllom/pyworkdir

Basic usage
-----------

Changing the current working directory::

    from pyworkdir import WorkDir

    with WorkDir("some_directory"):
        # everything in this context is run
        # in the specified directory
        pass


Directories are Customizable Classes
------------------------------------

`WorkDir` classes can be be customized by adding a file `workdir.py` to the directory.
All variables, functions, or classes defined in this file will be added as attributes of
the `WorkDir` instances.

For instance, consider the following `workdir.py` file::

    # -- workdir.py --
    def data_file(workdir, filename="data.csv"):
        return workdir/filename

The function can now be accessed from other code as follows::

    from pyworkdir import WorkDir

    with WorkDir() as wd:
        print(wd.data_file())

Note that the parameter `workdir` behaves like the `self` argument of the method. If `workdir` is not
an argument of the function, the function behaves like a static method.

By default, the `WorkDir` instance also recursively inherits attributes defined
in its parent directory's `workdir.py` files.
Therefore, subdirectories behave like subclasses.

Changing Environment Variables
------------------------------

Temporary changes of the environment::

    from pyworkdir import WorkDir

    with WorkDir(env={"MY_ENVIRONMENT_VARIABLE":"1"}):
        # in this context the environment variable is set
        pass

    # outside the context, it is not set any longer

Logging
-------

A logger is available::

    from pyworkdir import WorkDir
    import logging

    wd = WorkDir()
    wd.log("a INFO-level message")
    wd.log("a DEBUG-level message", logging.DEBUG)

By default, INFO-level and higher is printed to the console.
DEBUG-level output is only printed to a file `workdir.log`.


Modules
=======

workdir
-------

.. automodule:: pyworkdir.workdir
    :members:
    :undoc-members:
    :show-inheritance:


util
----

.. automodule:: pyworkdir.util
    :members:
    :undoc-members:
    :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
