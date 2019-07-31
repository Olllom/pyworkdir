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

Directories have a Command Line Interface
-----------------------------------------

Custom functions of the `WorkDir` are directly accessible from a terminal via the command `workdir`.
Before being called from the command line, all function parameters (except the reserved keywords `workdir` and `here`)
have to be declared as `Click options`_::

    # -- workdir.py --
    import click

    num_apples = 2

    @click.option("-c", type=int, default=12, help="A number (default:12)")
    @click.option("-s","--somebody", type=str, help="A name")
    def hello(count, somebody, workdir):
        """This function says hello."""
        workdir.num_apples += 1
        print(
            f"{count} times Hello! to {somebody}: "
            f"we have {workdir.num_apples} apples."
        )

Calling the function from the command line looks like this::

    foo@bar:~$  workdir hello --help
    Usage: workdir hello [OPTIONS]

      This function says hello.

    Options:
      -c, --count INTEGER  A number (default:12)
      -s, --somebody TEXT  A name
      --help               Show this message and exit.


    foo@bar:~$ workdir hello -s "you"
    12 times Hello! to you: we have 3 apples.


Writing `workdir.py` files like this makes it easy to define local functions that can be called both from inside python
and from a terminal. For the latter, the `workdir.py` behaves similar to a Makefile.

.. _Click options: https://click.palletsprojects.com/options/

Changing Environment Variables
------------------------------

Temporary changes of the environment::

    from pyworkdir import WorkDir

    with WorkDir(environment={"MY_ENVIRONMENT_VARIABLE":"1"}):
        # in this context the environment variable is set
        pass

    # outside the context, it is not set any longer


Yaml Files
----------

Environment variables and simple attributes can also be set through yml files.
The templates `{{ workdir }}` and `{{ here }}` are available and will be replaced by the working directory
instance and the directory that contains the yml file, respectively::

    # -- workdir.yml --
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

The attributes and environment variables get added to the WorkDir::

    import os

    with WorkDir() as wd:
        print(wd.my_number + 5, wd.my_tmpdir , wd.my_local_tmpfile)
        for el in wd.my_list:
             print(el)
        print(os.environ["VAR_ONE"])

Note that environment variables passed to the constructor have preference over those in a yml file.

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
