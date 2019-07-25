"""
Unit and regression test for the pyworkdir package.
"""

# Import package, test suite, and other packages as needed
import pyworkdir
import pytest
import sys

def test_pyworkdir_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "pyworkdir" in sys.modules
