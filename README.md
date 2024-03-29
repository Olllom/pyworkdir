pyworkdir
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.com/olllom/pyworkdir.svg)](https://travis-ci.com/olllom/pyworkdir)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)
[![Documentation Status](https://readthedocs.org/projects/pyworkdir/badge/?version=latest)](https://pyworkdir.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/olllom/pyworkdir/branch/master/graph/badge.svg)](https://codecov.io/gh/olllom/pyworkdir/branch/master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Maintainability](https://api.codeclimate.com/v1/badges/a9ff78c0b6ef41435c3d/maintainability)](https://codeclimate.com/github/Olllom/pyworkdir/maintainability)
[![python](https://img.shields.io/badge/python-3.6%2C%203.7-blue.svg)](https://anaconda.org/conda-forge/pyworkdir) 
[![Conda Recipe](https://img.shields.io/badge/recipe-pyworkdir-green.svg)](https://github.com/conda-forge/pyworkdir-feedstock)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/version.svg)](https://anaconda.org/conda-forge/pyworkdir)
<!-- These badges are cached too agressively on github.
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/platforms.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/downloads.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/pyworkdir)
-->
Python working directories

### Quickstart

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/installer/conda.svg)](https://anaconda.org/conda-forge/pyworkdir)

```bash
conda install -c conda-forge pyworkdir
```

#### Basic Usage

```python
from pyworkdir import WorkDir

with WorkDir("some_directory"):
    # everything in this context is run 
    # in the specified directory
    pass 
```

#### Directories are Customizable Classes

`WorkDir` classes can be be customized by adding a file `workdir.py` to the directory.
All variables, functions, or classes defined in this file will be added as attributes of
the `WorkDir` instances.

For instance, consider the following `workdir.py` file:
```python
# -- workdir.py --
def data_file(workdir, filename="data.csv"):
    return workdir/filename
```

The function can now be accessed from other code as follows:
```python
from pyworkdir import WorkDir

with WorkDir() as wd:
    print(wd.data_file())
```

Note that the parameter `workdir` behaves like the `self` argument of the method. If `workdir` is not
an argument of the function, the function behaves like a static method.

By default, the `WorkDir` instance also recursively inherits attributes defined
in its parent directory's `workdir.py` files.
Therefore, subdirectories behave like subclasses.

#### Directories have a Command Line Interface

Custom functions of the `WorkDir` are directly accessible from a terminal via the command `workdir`.
Before being called from the command line, all function parameters (except the reserved keywords `workdir` and `here`) 
have to be declared as [Click options](https://click.palletsprojects.com/options/).

```python
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
```
Calling the function from the command line looks like this:
```console
foo@bar:~$  workdir hello --help
Usage: workdir hello [OPTIONS]

  This function says hello.

Options:
  -c, --count INTEGER  A number (default:12)
  -s, --somebody TEXT  A name
  --help               Show this message and exit.


foo@bar:~$ workdir hello -s "you"
12 times Hello! to you: we have 3 apples.
```

Writing `workdir.py` files like this makes it easy to define local functions that can be called both from inside python 
and from a terminal. For the latter, the `workdir.py` behaves similar to a Makefile.

To suppress generation of the command line interface for a function, pyworkdir provides a `no_cli` decorator.
```python
    # -- workdir.py --

    from pyworkdir import no_cli

    @no_cli
    def a_function_without_command_line_interface():
        pass
```

#### Changing Environment Variables

```python
from pyworkdir import WorkDir

with WorkDir(environment={"MY_ENVIRONMENT_VARIABLE":"1"}):
    # in this context the environment variable is set
    pass

# outside the context, it is not set any longer
```


#### Yaml Files

Environment variables and simple attributes can also be set through yml files.
The templates `{{ workdir }}` and `{{ here }}` are available and will be replaced by the working directory
instance and the directory that contains the yml file, respectively.

```
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
commands:
    echo: echo Hello // print Hello to the command line

```

The commands are shortcuts for terminal commands that can be called from python and from the command line.
Everything after `//` is used as a documentation string for the command line interface.
The attributes and environment variables get added to the WorkDir.

```python
from pyworkdir import WorkDir
with WorkDir() as wd:
    print(wd.my_number + 5, wd.my_tmpdir , wd.my_local_tmpfile)
    for el in wd.my_list:
        print(el)
    print(os.environ["VAR_ONE"])
```

Note that environment variables passed to the constructor have preference over those in a yml file.


#### Logging

```python
from pyworkdir import WorkDir
import logging

wd = WorkDir()
wd.log("a INFO-level message")
wd.log("a DEBUG-level message", logging.DEBUG)
```
By default, INFO-level and higher is printed to the console.
DEBUG-level output is only printed to a file `workdir.log`.

### Documentation

[![Documentation Status](https://readthedocs.org/projects/pyworkdir/badge/?version=latest)](https://pyworkdir.readthedocs.io/en/latest/?badge=latest)


### Copyright

Copyright (c) 2019, Andreas Krämer


#### Acknowledgements

External Packages:
 * [Click](https://click.palletsprojects.com/) - Command line interface
 * [Jinja2](https://palletsprojects.com/p/jinja/) - Template engine
 * [PyYaml](https://pyyaml.org) - Yaml parser
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.0.
