import pytest

from configx.utils.evaluation_utils import get_template_variables


def test_get_template_variables():
    """
    When string has variable between {} or {{}}
    Should return tree_path of that variable
    """
    assert get_template_variables("foo bar") == ()
    assert get_template_variables("foo {bar}") == ("bar",)
    assert get_template_variables("{bar} foo") == ("bar",)
    assert get_template_variables("foo {{ bar }}") == ("bar",)
    assert get_template_variables("foo {bar} spam {{eggs}}") == ("bar", "eggs")
    assert get_template_variables("foo {{bar} spam {eggs}}") == ("bar", "eggs")
    assert get_template_variables("foo { bar.spam }") == ("bar.spam",)
