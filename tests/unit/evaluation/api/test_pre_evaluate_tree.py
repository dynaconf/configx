"""
Tests the correctness of evaluation:pre_evaluate_tree(setting_tree) by checking:
    - trivial conversions: raw -> real
    - lazy conversions: raw -> lazy
    - correct dependecy_graph is returned
"""

from configx.core.setting_tree import SettingTree
from configx.services.evaluation.api import pre_evaluate_tree
from configx.types import NOT_EVALUATED, LazyValue


def test_has_dependencies():
    data = {
        "a": "A",
        "b": {"foo": "@format foo_{this.a}"},
        "c": [1, 2, {"d": "@int 123"}],
    }
    setting_tree = SettingTree()
    setting_tree.populate(data)

    dependency_graph = pre_evaluate_tree(setting_tree)
    dependency_graph_list = [v for v in dependency_graph.items()]

    assert len(dependency_graph_list) == 2
    assert dependency_graph_list == [
        (("root", "a"), []),
        (("root", "b", "foo"), [("root", "a")]),
    ]

    assert setting_tree.get_node(("a",)).element.real_value == "A"
    assert setting_tree.get_node(("c", 2, "d")).element.real_value == 123

    a_foo_node = setting_tree.get_node(("b", "foo"))
    assert isinstance(a_foo_node.element.raw_value, LazyValue)
    assert a_foo_node.element.real_value == NOT_EVALUATED
    assert a_foo_node.element.raw_value.string == "foo_{this.a}"


def test_no_dependencies():
    data = {
        "a": "A",
        "b": {"foo": "@format foo"},
        "c": [1, 2, {"d": "@int 123"}],
    }
    setting_tree = SettingTree()
    setting_tree.populate(data)

    dependency_graph = pre_evaluate_tree(setting_tree)
    dependency_graph_list = [v for v in dependency_graph.items()]

    assert len(dependency_graph_list) == 0
    assert dependency_graph_list == []
    assert setting_tree.get_node(("a",)).element.real_value == "A"
    assert setting_tree.get_node(("c", 2, "d")).element.real_value == 123
    assert setting_tree.get_node(("b", "foo")).element.real_value == "foo"
