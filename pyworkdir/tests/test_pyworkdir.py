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
