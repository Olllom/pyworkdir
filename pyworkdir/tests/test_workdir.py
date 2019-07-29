"""
Unit and regression test for the pyworkdir package.
"""

from pyworkdir import WorkDir, WorkDirException
import pytest
import pathlib
import textwrap
import os


def test_change_directory(tmpdir):
    """Test that the working directory changes the directory correctly"""
    surrounding_path = os.getcwd()
    with WorkDir(tmpdir):
        assert os.getcwd() == str(tmpdir)
    assert os.getcwd() == surrounding_path


def test_create_directory(tmpdir):
    """Check mkdir parameter"""
    dir = tmpdir/"subdir"
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
        with WorkDir(tmpdir):
            assert False


def test_truediv(tmpdir):
    """Test the division operator."""
    with WorkDir(tmpdir) as wd:
        assert str(wd/"file.txt") == tmpdir/"file.txt"


def test_len(tmpdir):
    """Test length operator"""
    with WorkDir(tmpdir) as wd:
        assert len(wd) == 0
        os.mkdir(wd/"a")
        assert len(wd) == 1


def test_files(tmpdir):
    """Test WorkDir.files()"""
    with WorkDir(tmpdir) as wd:
        (wd.path/"a").touch()
        (wd.path/"b").touch()
        (wd.path/"c").touch()
        os.mkdir(wd/"dir")
        assert len([f for f in wd.files()]) == 3
        assert all(isinstance(f, pathlib.Path) for f in wd.files())
        assert all(os.path.dirname(f) == "" for f in wd.files())
        assert all(os.path.dirname(f) == str(tmpdir) for f in wd.files(abs=True))


def test_str(tmpdir):
    wd = WorkDir(tmpdir)
    assert str(wd) == str(tmpdir)


def test_import_from_workdir_py(tmpdir):
    """Test that workdir.py file is read and added to the workdir"""
    contents = textwrap.dedent(
        """
        import os
        
        def jambalaya(a,b):
            import sys
            return a+b
            
        print("JAMBALAYA")
        
        
        class Jambalaya(object):
            pass
        """
    )
    with open(tmpdir/"workdir.py", "w") as pyfile:
        pyfile.write(contents)
    wd = WorkDir(tmpdir)
    assert hasattr(wd, "jambalaya")
    assert hasattr(wd, "Jambalaya")
    assert callable(wd.jambalaya)
    assert isinstance(wd.Jambalaya, type)
    assert not hasattr(wd, "sys")
    assert not hasattr(wd, "os")
    assert wd.jambalaya(2,5) == 7


def test_import_imports(tmpdir):
    """Test that top-level imports are known to the function."""
    contents = textwrap.dedent(
        """
        import wave

        def jambalaya(a,b):
            assert hasattr(wave, "Chunk")  # to make sure that top level imports are recognized
            return a+b
        """
    )
    with open(tmpdir / "workdir.py", "w") as pyfile:
        pyfile.write(contents)
    wd = WorkDir(tmpdir)
    assert hasattr(wd, "jambalaya")
    assert wd.jambalaya(2, 5) == 7


def test_failure_import_with_workdir(tmpdir):
    """Test that bugs in the functions are detected."""
    contents = textwrap.dedent(
        """
        def jambalaya(a, b):
            assert hasattr(wave, "Chunk")  # to make sure that top level imports are recognized
            return a+b
        """
    )
    with open(tmpdir / "workdir.py", "w") as pyfile:
        pyfile.write(contents)
    wd = WorkDir(tmpdir)
    with pytest.raises(NameError):
        wd.jambalaya(2, 5)


def test_function_added_as_method(tmpdir):
    """Test that workdir is accessible for functions that use workdir"""
    contents = textwrap.dedent(
        """
        def jambalaya(a, workdir, b):
            return workdir.path, a+b
        """
    )
    with open(tmpdir / "workdir.py", "w") as pyfile:
        pyfile.write(contents)
    wd = WorkDir(tmpdir)
    path, sum = wd.jambalaya(2, 5)
    assert isinstance(path, pathlib.Path)
    assert str(path) == str(tmpdir)


def test_function_with_kwargs_added_as_method(tmpdir):
    """Test that workdir is accessible for functions that use workdir"""
    contents = textwrap.dedent(
        """
        def jambalaya(a, workdir, b=4):
            return workdir.path, a+b
        """
    )
    with open(tmpdir / "workdir.py", "w") as pyfile:
        pyfile.write(contents)
    wd = WorkDir(tmpdir)
    path, sum = wd.jambalaya(2, 5)
    assert isinstance(path, pathlib.Path)
    assert sum == 7
    assert str(path) == str(tmpdir)
    path, sum = wd.jambalaya(2)
    assert sum == 6


def test_vars_and_classes_from_pyfile(tmpdir):
    """Test that variables and classes from python files get added """
    contents = textwrap.dedent(
        """
        import pyworkdir
        
        a = 2
        
        class A(pyworkdir.WorkDir):
            pass
        """
    )
    with open(tmpdir / "workdir.py", "w") as pyfile:
        pyfile.write(contents)
    wd = WorkDir(tmpdir)
    assert hasattr(wd, "A")
    assert hasattr(wd, "a")
    assert wd.a == 2
    assert issubclass(wd.A, WorkDir)
    assert isinstance(wd.A(), WorkDir)


def test_recursive_pyfile(tmpdir):
    """Test that pyfiles are loaded recursively and that more specific settings override more general ones."""
    contents = textwrap.dedent(
        """
        a = 2
        b = 2
        """
    )
    contents_parent = textwrap.dedent(
        """
        a = 3
        c = 3
        """
    )
    os.mkdir(tmpdir/"subdir")
    with open(tmpdir/"subdir/workdir.py", "w") as f:
        f.write(contents)
    with open(tmpdir/"workdir.py", "w") as f:
        f.write(contents_parent)
    wd = WorkDir(tmpdir/"subdir")
    assert hasattr(wd, "a")
    assert hasattr(wd, "b")
    assert hasattr(wd, "c")
    assert wd.a == 2
    assert wd.b == 2
    assert wd.c == 3
    # test custom attributes dict
    assert wd.custom_attributes["a"] == os.path.realpath(tmpdir/"subdir/workdir.py")
    assert wd.custom_attributes["b"] == os.path.realpath(tmpdir/"subdir/workdir.py")
    assert wd.custom_attributes["c"] == os.path.realpath(tmpdir/"workdir.py")


def test_here_argument(tmpdir):
    """Test that the `here` parameter is replaced by the directory of the workdir.py"""
    contents = textwrap.dedent(
        """
        def some_path(here, workdir, filename):
            return workdir/filename, here/filename
        """
    )
    with open(tmpdir/"workdir.py", "w") as f:
        f.write(contents)
    subdir = WorkDir(tmpdir/"subdir")
    wd = WorkDir(tmpdir)
    sub_wd, sub_here = subdir.some_path("file.txt")
    parent_wd, parent_here = wd.some_path("file.txt")
    assert str(parent_here) == os.path.join(tmpdir, "file.txt")
    assert sub_here == parent_here
    assert parent_here == parent_wd
    assert sub_wd == subdir.path/"file.txt"

