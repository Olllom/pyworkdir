pyworkdir
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.com/olllom/pyworkdir.png)](https://travis-ci.com/olllom/pyworkdir)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)
[![codecov](https://codecov.io/gh/olllom/pyworkdir/branch/master/graph/badge.svg)](https://codecov.io/gh/olllom/pyworkdir/branch/master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/version.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/downloads.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/platforms.svg)](https://anaconda.org/conda-forge/pyworkdir)
[![Maintainability](https://api.codeclimate.com/v1/badges/a9ff78c0b6ef41435c3d/maintainability)](https://codeclimate.com/github/Olllom/pyworkdir/maintainability)

Python working directories.

### Quickstart

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyworkdir/badges/installer/conda.svg)](https://conda.anaconda.org/conda-forge)
#### Basic Usage

```python
from pyworkdir import WorkDir

with WorkDir("some_directory"):
    # everything in this context is run 
    # in the specified directory
    pass 
```

### Documentation

[![Documentation Status](https://readthedocs.org/projects/pyworkdir/badge/?version=latest)](https://pyworkdir.readthedocs.io/en/latest/?badge=latest)


### Copyright

Copyright (c) 2019, Andreas Krämer


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.0.
