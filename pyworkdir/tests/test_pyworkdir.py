"""
Unit and regression test for the pyworkdir package.
"""

from pyworkdir import WorkDir
import pytest
import sys
import os


def test_change_directory(tmpdir):
    """Test that the working directory changes the directory correctly"""
    this_path = os.getcwd()
    with WorkDir(str(tmpdir)):
        assert os.getcwd() == str(tmpdir)
    assert os.getcwd() == this_path


def test_error_in_context(tmpdir):
    """Test that an exception in the context is forwarded."""
    with WorkDir(str(tmpdir)):
        with pytest.raises(AssertionError):
            assert False
