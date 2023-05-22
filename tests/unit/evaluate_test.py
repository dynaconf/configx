from typing import Any, NamedTuple

from configx.core.setting_tree import Node, SettingTree
from configx.operations.evaluation import (
    NOT_EVALUATED,
    pre_evaluate_node,
    pre_evaluate_tree,
)
from configx.operations.utils.converters import get_converter
from configx.types import SimpleTypes


class PreEvaluateExpected(NamedTuple):
    input: str
    raw: str | tuple
    real: Any
    dep_graph_len: int = 0


P = PreEvaluateExpected

fn = get_converter

casting_testcases = {
    "cast-int": P(input="@int 123", raw=(fn("int"), "123"), real=123),
    "cast-float": P(input="@float 123", raw=(fn("float"), "1.23"), real=1.23),
    "cast-bool-false": P(input="@bool false", raw=(fn("bool"), "1.23"), real=False),
    "cast-bool-true": P(input="@bool true", raw=(fn("bool"), "1.23"), real=True),
}

composability_testcases = {
    "compound-int-format": P(
        input="@int @format 123", raw=(fn("int"), fn("format"), "123"), real=123
    ),
    "compound-int-jinja": P(
        input="@int @jinja 123", raw=(fn("int"), fn("jinja"), "123"), real=123
    ),
    "compound-int-jinja": P(
        input="@int @jinja 123", raw=(fn("int"), fn("jinja"), "123"), real=123
    ),
}

dependency_format_testcases = {
    "dependency-format-one-sub": P(
        input="@format {this.foo.bar}",
        raw=(fn("format"), "{this['foo']['bar']}"),
        real=NOT_EVALUATED,
        dep_graph_len=1,
    ),
    "dependency-format-two-subs": P(
        input="@format {this.foo.bar} {this.spam.eggs}",
        raw=(fn("format"), "{this['foo']['bar']} {this['spam']['eggs']}"),
        real=NOT_EVALUATED,
        dep_graph_len=2,
    ),
    "dependency-format-list-type": P(
        input="@format {this.foo.0}",
        raw=(fn("format"), "{this['foo'][0]}"),
        real=NOT_EVALUATED,
        dep_graph_len=1,
    ),
}

dependency_jinja_testcases = {
    "dependency-jinja-one-sub": P(
        input="@jinja {{ this.foo.bar }}",
        raw=(fn("jinja"), "{{ this['foo']['bar'] }}"),
        real=NOT_EVALUATED,
        dep_graph_len=1,
    ),
    "dependency-jinja-two-subs": P(
        input="@jinja {{ this.foo.bar }} {{ this.spam.eggs }}",
        raw=(fn("jinja"), "{this['foo']['bar']} {this['spam']['eggs']}"),
        real=NOT_EVALUATED,
        dep_graph_len=2,
    ),
    "dependency-jinja-list-type": P(
        input="@jinja {{ this.foo.0 }}",
        raw=(fn("jinja"), "{{ this['foo'][0] }}"),
        real=NOT_EVALUATED,
        dep_graph_len=1,
    ),
}


# TODO make some utility to load previous format into @pytest.parametrize
def test_pre_evaluate_node():
    input = "hello"
    expected_raw = ""
    expected_real = None
    expected_d_len = 0

    st = SettingTree()
    data = {"value": input}
    st.populate(data)  # type: ignore (why?)

    node = st._get_node(("value",))

    d = pre_evaluate_node(node)

    assert node.element.raw_value == expected_raw
    assert node.element.real_value == expected_real
    assert len(d) == expected_d_len


# TODO add testcases for failure
def test_pre_evaluate_node_raises():
    input = "hello"
    expected_raw = ""
    expected_real = None
    expected_d_len = 0

    st = SettingTree()
    data = {"value": input}
    st.populate(data)  # type: ignore (why?)

    node = st._get_node(("value",))

    d = pre_evaluate_node(node)

    assert node.element.raw_value == expected_raw
    assert node.element.real_value == expected_real
    assert len(d) == expected_d_len
