"""
Tests the correctness of evaluation:pre_evaluate_node(node) by checking:
    - the Setting object state after execution
    - returned dependency_edges

This uses a custom parametrization method to help with state checking.
"""
from typing import Any, NamedTuple

import pytest

from configx.core.setting_tree import SettingTree
from configx.services.evaluation.api import pre_evaluate_node
from configx.types import NOT_EVALUATED, LazyValue, TreePath

pytestmark = pytest.mark.module_api


class _TestCase(NamedTuple):
    """
    Given:
        node.element.raw_value = @input (eg, '@token foo')
    Executing:
        pre_evaluate_node(node)
    Should:
        set node.setting.raw_value.string: @lazy_string
        set node.setting.real_value: @real_value
        return @depenendcies of Node
    """

    input: str
    lazy_string: str
    real_value: Any
    dependencies: list[TreePath] = []


casting_testcases = {
    "int": _TestCase("@int 123", "123", 123),
    "float": _TestCase("@float 1.23", "1.23", 1.23),
    "bool-false": _TestCase("@bool true", "true", True),
    "bool-true": _TestCase("@bool false", "false", False),
}

composability_testcases = {
    "int-format": _TestCase("@int @format 123", "123", 123),
    "float-jinja": _TestCase("@float @jinja 12.3", "12.3", 12.3),
    "bool-jinja": _TestCase("@bool @jinja false", "false", False),
    "str-jinja": _TestCase("@str @int 123", "123", "123"),
}

dependency_format_testcases = {
    "one-substitution": _TestCase(
        input="@format {this.foo.bar}",
        lazy_string="{this.foo.bar}",
        real_value=NOT_EVALUATED,
        dependencies=[("foo", "bar")],
    ),
    "two-substitutions": _TestCase(
        input="@format {this.foo.bar} {this.spam.eggs}",
        lazy_string="{this.foo.bar} {this.spam.eggs}",
        real_value=NOT_EVALUATED,
        dependencies=[("foo", "bar"), ("spam", "eggs")],
    ),
    "sub-with-list-access": _TestCase(
        input="@format {this.foo.0}",
        lazy_string="{this.foo.0}",
        real_value=NOT_EVALUATED,
        dependencies=[("foo", 0)],
    ),
}

dependency_jinja_testcases = {
    "one-substitution": _TestCase(
        input="@jinja {{ this.foo.bar }}",
        lazy_string="{{ this.foo.bar }}",
        real_value=NOT_EVALUATED,
        dependencies=[("foo", "bar")],
    ),
    "two-substitution": _TestCase(
        input="@jinja {{ this.foo.bar }} {{ this.spam.eggs }}",
        lazy_string="{{ this.foo.bar }} {{ this.spam.eggs }}",
        real_value=NOT_EVALUATED,
        dependencies=[("foo", "bar"), ("spam", "eggs")],
    ),
    "list-type": _TestCase(
        input="@jinja {{ this.foo.0 }}",
        lazy_string="{{ this.foo.0 }}",
        real_value=NOT_EVALUATED,
        dependencies=[("foo", 0)],
    ),
}


def use_testcase(data: dict[str, _TestCase]):
    """Return dict to be unpacked in @pytest.mark.parametrize params"""
    argnames = [*_TestCase._fields]
    argvalues = []
    for test_id, expected in data.items():
        argvalues.append(pytest.param(*expected, id=test_id))
    return argnames, argvalues


@pytest.mark.parametrize(*use_testcase(casting_testcases))
def test_casting(input, lazy_string, real_value, dependencies):
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})
    node = setting_tree.get_node(("value",))

    dependency_edges = pre_evaluate_node(node)

    assert isinstance(node.element._raw_value, LazyValue)
    assert node.element._raw_value.string == lazy_string
    assert node.element.real_value == real_value
    assert dependency_edges == dependencies


@pytest.mark.parametrize(*use_testcase(composability_testcases))
def test_composability(input, lazy_string, real_value, dependencies):
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})
    node = setting_tree.get_node(("value",))

    dependency_edges = pre_evaluate_node(node)

    assert isinstance(node.element._raw_value, LazyValue)
    assert node.element._raw_value.string == lazy_string
    assert node.element.real_value == real_value
    assert dependency_edges == dependencies


@pytest.mark.parametrize(*use_testcase(dependency_format_testcases))
def test_format(input, lazy_string, real_value, dependencies):
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})
    node = setting_tree.get_node(("value",))

    dependency_edges = pre_evaluate_node(node)
    depends_on_list = [d.depends_on for d in dependency_edges]

    assert isinstance(node.element._raw_value, LazyValue)
    assert node.element._raw_value.string == lazy_string
    assert node.element.real_value == real_value
    assert depends_on_list == dependencies


@pytest.mark.parametrize(*use_testcase(dependency_jinja_testcases))
def test_jinja(input, lazy_string, real_value, dependencies):
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})  # type: ignore
    node = setting_tree.get_node(("value",))

    dependency_edges = pre_evaluate_node(node)
    result_dependencies = [d.depends_on for d in dependency_edges]

    assert isinstance(node.element._raw_value, LazyValue)
    assert node.element._raw_value.string == lazy_string
    assert node.element.real_value == real_value
    assert result_dependencies == dependencies


# TODO add testcases for failure
@pytest.mark.skip
def test_raises():
    input = "hello"
    expected_raw = ""
    expected_real = None
    expected_d_len = 0

    st = SettingTree()
    data = {"value": input}
    st.populate(data)

    node = st.get_node(("value",))

    d = pre_evaluate_node(node)

    assert node.element._raw_value == expected_raw
    assert node.element.real_value == expected_real
    assert len(d) == expected_d_len
