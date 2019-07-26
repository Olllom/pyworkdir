"""
Unit and regression test for the pyworkdir package.
"""

from pyworkdir import WorkDir, WorkDirException
import pytest
import pathlib
import os


def test_change_directory(tmpdir):
    """Test that the working directory changes the directory correctly"""
    surrounding_path = os.getcwd()
    with WorkDir(str(tmpdir)):
        assert os.getcwd() == str(tmpdir)
    assert os.getcwd() == surrounding_path


def test_create_directory(tmpdir):
    """Check mkdir parameter"""
    dir = os.path.join(str(tmpdir), "subdir")
    wd = WorkDir(dir, mkdir=False)
    assert not wd.path.exists()
    wd = WorkDir(dir, mkdir=True)
    assert wd.path.exists()
    wd = WorkDir(dir, mkdir=True)
    # check failures
    (wd.path/"a").touch()
    with pytest.raises(WorkDirException):
        WorkDir(wd.path/"a", mkdir=True)


def test_error_in_context(tmpdir):
    """Test that an exception in the context is forwarded."""
    with pytest.raises(AssertionError):
        with WorkDir(str(tmpdir)):
            assert False


def test_truediv(tmpdir):
    """Test the division operator."""
    with WorkDir(str(tmpdir)) as wd:
        assert str(wd/"file.txt") == os.path.join(str(tmpdir), "file.txt")


def test_len(tmpdir):
    """Test length operator"""
    with WorkDir(str(tmpdir)) as wd:
        assert len(wd) == 0
        os.mkdir(wd/"a")
        assert len(wd) == 1


def test_files(tmpdir):
    """Test WorkDir.files()"""
    with WorkDir(str(tmpdir)) as wd:
        (wd.path/"a").touch()
        (wd.path/"b").touch()
        (wd.path/"c").touch()
        os.mkdir(wd/"dir")
        assert len([f for f in wd.files()]) == 3
        assert all(isinstance(f, pathlib.Path) for f in wd.files())
        assert all(os.path.dirname(f) == "" for f in wd.files())
        assert all(os.path.dirname(f) == str(tmpdir) for f in wd.files(abs=True))
