"""
Tests for utilities.
"""

from pyworkdir.util import add_method


def test_make_method():
    class A(object):
        def __init__(self, value):
            self.internal_value = value

    def function_to_be_method(b, instance):
        return b + instance.internal_value

    instance = A(2)
    add_method(instance, function_to_be_method, "instance")
    assert hasattr(instance, "function_to_be_method")
    assert instance.function_to_be_method(3) == 5

    instance2 = A(3)
    assert not hasattr(instance2, "function_to_be_method")

