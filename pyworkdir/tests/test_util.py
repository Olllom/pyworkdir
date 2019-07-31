"""
Tests for utilities.
"""

from pyworkdir.util import add_function


def test_add_method_replace_args():
    """Testing a function to a class as a method."""
    class A(object):
        def __init__(self, value):
            self.internal_value = value

    def function_to_be_method(b, instance):
        return b + instance.internal_value

    instance = A(2)
    add_function(instance, function_to_be_method, replace_args={"instance": instance})
    assert hasattr(instance, "function_to_be_method")
    assert instance.function_to_be_method(3) == 5

    instance2 = A(3)
    assert not hasattr(instance2, "function_to_be_method")


def test_add_staticmethod():
    """Test adding custom static methods."""
    class A(object):
        pass

    def function_to_be_method(b):
        return b
    instance = A()

    add_function(instance, function_to_be_method)
    assert function_to_be_method(3) == 3


def test_add_method_click_options():
    """Test if replaced args are added as hidden click options."""
    class A(object):
        def __init__(self, value):
            self.internal_value = value

    def function_to_be_method(b, instance, o_ther):
        return b + instance.internal_value

    instance = A(2)
    add_function(instance, function_to_be_method, replace_args={"instance": instance, "o_ther": 2})
    assert hasattr(instance, "function_to_be_method")
    assert hasattr(instance.function_to_be_method, "__click_params__")
    options = instance.function_to_be_method.__click_params__
    assert len(options) == 2
    assert options[0].name == "instance"
    assert options[1].name == "o_ther"
