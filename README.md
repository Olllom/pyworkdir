pyworkdir
==============================
[//]: # (Badges)
[![Travis Build Status](https://travis-ci.org/olllom/pyworkdir.png)](https://travis-ci.org/olllom/pyworkdir)
[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)](https://ci.appveyor.com/api/projects/status/apgjk3oy6vylm8jv?svg=true)
[![codecov](https://codecov.io/gh/olllom/pyworkdir/branch/master/graph/badge.svg)](https://codecov.io/gh/olllom/pyworkdir/branch/master)

Python working directories.

### Quickstart

#### Basic Usage

```python
    from pyworkdir import WorkDir
    
    with WorkDir("some_directory"):
        # everything in this context is run 
        # in the specified directory
        pass 
```

### Copyright

Copyright (c) 2019, Andreas Krämer


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.0.
