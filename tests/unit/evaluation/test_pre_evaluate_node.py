from typing import Any, NamedTuple

import pytest

from configx.services.evaluation.evaluate import pre_evaluate_node, pre_evaluate_tree
from configx.services.evaluation.processors_core import get_processor
from configx.core.setting_tree import Node, SettingTree
from configx.types import NOT_EVALUATED, LazyValue, RawProcessor, SimpleTypes


class TestCase(NamedTuple):
    """
    Given:
        node.element.raw_value = @input (eg, '@token foo')
    Executing:
        pre_evaluate_node(node)
    Should:
        set node.setting.raw_value:
            LazyValue(
                processors = get_processor(@lazy_processor_name),
                string = @lazy_string
            )
        set node.setting.real_value: @real_value
        return depenendcy_edges (len == @dependecy_edges_len)
    """

    input: str
    lazy_processor_names: list[str]
    lazy_string: str
    real_value: Any
    dependecy_edges_len: int = 0


casting_testcases = {
    "cast-int": TestCase("@int 123", ["int"], "123", 123),
    "cast-float": TestCase("@float 1.23", ["float"], "1.23", 1.23),
    "cast-bool-false": TestCase("@bool true", ["bool"], "true", True),
    "cast-bool-true": TestCase("@bool false", ["bool"], "false", False),
}

# composability_testcases = {
#     "compound-int-format": TestCase(
#         input="@int @format 123", raw=(getcon("int"), getcon("format"), "123"), real=123
#     ),
#     "compound-int-jinja": TestCase(
#         input="@int @jinja 123", raw=(getcon("int"), getcon("jinja"), "123"), real=123
#     ),
#     "compound-int-jinja": TestCase(
#         input="@int @jinja 123", raw=(getcon("int"), getcon("jinja"), "123"), real=123
#     ),
# }

# dependency_format_testcases = {
#     "dependency-format-one-sub": TestCase(
#         input="@format {this.foo.bar}",
#         raw=(getcon("format"), "{this['foo']['bar']}"),
#         real=NOT_EVALUATED,
#         dep_graph_len=1,
#     ),
#     "dependency-format-two-subs": TestCase(
#         input="@format {this.foo.bar} {this.spam.eggs}",
#         raw=(getcon("format"), "{this['foo']['bar']} {this['spam']['eggs']}"),
#         real=NOT_EVALUATED,
#         dep_graph_len=2,
#     ),
#     "dependency-format-list-type": TestCase(
#         input="@format {this.foo.0}",
#         raw=(getcon("format"), "{this['foo'][0]}"),
#         real=NOT_EVALUATED,
#         dep_graph_len=1,
#     ),
# }

# dependency_jinja_testcases = {
#     "dependency-jinja-one-sub": TestCase(
#         input="@jinja {{ this.foo.bar }}",
#         raw=(getcon("jinja"), "{{ this['foo']['bar'] }}"),
#         real=NOT_EVALUATED,
#         dep_graph_len=1,
#     ),
#     "dependency-jinja-two-subs": TestCase(
#         input="@jinja {{ this.foo.bar }} {{ this.spam.eggs }}",
#         raw=(getcon("jinja"), "{this['foo']['bar']} {this['spam']['eggs']}"),
#         real=NOT_EVALUATED,
#         dep_graph_len=2,
#     ),
#     "dependency-jinja-list-type": TestCase(
#         input="@jinja {{ this.foo.0 }}",
#         raw=(getcon("jinja"), "{{ this['foo'][0] }}"),
#         real=NOT_EVALUATED,
#         dep_graph_len=1,
#     ),
# }


def use_testcase(data: dict[str, TestCase]):
    """Return dict to be unpacked in @pytest.mark.parametrize params"""
    argnames = [*TestCase._fields]
    argvalues = []
    for test_id, expected in data.items():
        argvalues.append(pytest.param(*expected, id=test_id))
    return argnames, argvalues


@pytest.mark.parametrize(*use_testcase(casting_testcases))
def test_pre_evaluate_node__casting(
    input, lazy_string, lazy_processor_names, real_value, dependecy_edges_len
):
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})
    node = setting_tree.get_node(("value",))

    dependency_edges = pre_evaluate_node(node)

    assert isinstance(node.element.raw_value, LazyValue)
    assert node.element.raw_value.string == lazy_string
    assert node.element.raw_value.operators == [
        get_processor(c) for c in lazy_processor_names
    ]
    assert node.element.real_value == real_value
    assert len(dependency_edges) == dependecy_edges_len


# @pytest.mark.parametrize(*use_testcase(composability_testcases))
@pytest.mark.skip
def test_pre_evaluate_node__composability(input, raw, real, dep_graph_len):
    """
    Given input
    Expect Setting state (raw and real values) and dependencies length
    """
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})  # type: ignore (why?)
    node = setting_tree.get_node(("value",))

    dependency_graph = pre_evaluate_node(node)

    assert node.element.raw_value == raw
    assert node.element.real_value == real
    assert len(dependency_graph) == dep_graph_len


# @pytest.mark.parametrize(*use_testcase(dependency_format_testcases))
@pytest.mark.skip
def test_pre_evaluate_node__format(input, raw, real, dep_graph_len):
    """
    Given input
    Expect Setting state (raw and real values) and dependencies length
    """
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})  # type: ignore (why?)
    node = setting_tree.get_node(("value",))

    dependency_graph = pre_evaluate_node(node)

    assert node.element.raw_value == raw
    assert node.element.real_value == real
    assert len(dependency_graph) == dep_graph_len


# @pytest.mark.parametrize(*use_testcase(dependency_jinja_testcases))
@pytest.mark.skip
def test_pre_evaluate_node__jinja(input, raw, real, dep_graph_len):
    """
    Given input
    Expect Setting state (raw and real values) and dependencies length
    """
    setting_tree = SettingTree()
    setting_tree.populate({"value": input})  # type: ignore (why?)
    node = setting_tree.get_node(("value",))

    dependency_graph = pre_evaluate_node(node)

    assert node.element.raw_value == raw
    assert node.element.real_value == real
    assert len(dependency_graph) == dep_graph_len


# TODO add testcases for failure
@pytest.mark.skip
def test_pre_evaluate_node__raises():
    input = "hello"
    expected_raw = ""
    expected_real = None
    expected_d_len = 0

    st = SettingTree()
    data = {"value": input}
    st.populate(data)  # type: ignore (why?)

    node = st.get_node(("value",))

    d = pre_evaluate_node(node)

    assert node.element.raw_value == expected_raw
    assert node.element.real_value == expected_real
    assert len(d) == expected_d_len
