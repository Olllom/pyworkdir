"""
pyworkdir
Python working directories.
"""

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions

# Add imports here
from pyworkdir.util import WorkDirException
from pyworkdir.workdir import WorkDir



