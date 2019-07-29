pyworkdir
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.com/olllom/pyworkdir.png)](https://travis-ci.com/olllom/pyworkdir)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)
[![codecov](https://codecov.io/gh/olllom/pyworkdir/branch/master/graph/badge.svg)](https://codecov.io/gh/olllom/pyworkdir/branch/master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![Maintainability](https://api.codeclimate.com/v1/badges/a9ff78c0b6ef41435c3d/maintainability)](https://codeclimate.com/github/Olllom/pyworkdir/maintainability)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/version.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/downloads.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/platforms.svg)](https://anaconda.org/conda-forge/pyworkdir)

Python working directories.

### Quickstart

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/installer/conda.svg)](https://conda.anaconda.org/conda-forge)

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

#### Advanced Features

##### Custom Attributes
Instances of `WorkDir` can be be customized by adding a file `workdir.py` to the directory.
All variables, functions, or classes defined in this file will be added as attributes of 
the `WorkDir` instance.

For instance, consider the following `workdir.py` file
```python
# -- workdir.py --
def data_files(workdir, suffix=".dat"):
    for f in workdir.files():
        if f.endswith(suffix):
            yield f
```

The function `data_files` can now be accessed from other code as follows:

```python 
with WorkDir() as wd:
    for data_file in wd.data_files():
        print(data_file)
```
Note that the function parameter `workdir` behaves as the `self` argument of the method. If `workdir` is not 
an argument of the function, it behaves like a static method.

By default, the `WorkDir` instance also recursively inherits attributes defined in its parent directory's `workdir.py` files.
Therefore, subdirectories behave like subclasses.

##### Yaml Files

##### Changing Environment Variables
To be done.

### Documentation

[![Documentation Status](https://readthedocs.org/projects/pyworkdir/badge/?version=latest)](https://pyworkdir.readthedocs.io/en/latest/?badge=latest)


### Copyright

Copyright (c) 2019, Andreas Krämer


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.0.
