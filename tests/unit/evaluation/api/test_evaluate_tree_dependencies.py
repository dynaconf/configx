"""
Tests the correctness of evaluation:evaluate_tree(setting_tree) by checking:
    - real value only
"""

from graphlib import CycleError

import pytest

from configx.core.setting_tree import SettingTree
from configx.exceptions import MissingContextValue
from configx.services.evaluation.api import (
    evaluate_tree,
    evaluate_tree_dependencies,
    pre_evaluate_tree,
)
from configx.types import NOT_EVALUATED, LazyValue


def test_has_dependencies_and_sufficient_context():
    data = {
        "a": "A",
        "b": {"foo": "@format foo_{this.a}"},
        "c": [123, 456, {"d": "@format version-{this.c.0}"}],
    }
    setting_tree = SettingTree()
    setting_tree.populate(data)

    dependency_graph = pre_evaluate_tree(setting_tree)
    evaluate_tree_dependencies(setting_tree, dependency_graph)

    assert setting_tree.get_node(("a",)).element.real_value == "A"
    assert setting_tree.get_node(("b", "foo")).element.real_value == "foo_A"
    assert setting_tree.get_node(("c", 2, "d")).element.real_value == "version-123"


def test_has_dependencies_and_insufficient_context():
    data = {
        "a": "A",
        "b": {"foo": "@format foo_{this.version}"},
    }
    setting_tree = SettingTree()
    setting_tree.populate(data)
    dependency_graph = pre_evaluate_tree(setting_tree)
    with pytest.raises(MissingContextValue):
        evaluate_tree_dependencies(setting_tree, dependency_graph)


def test_has_cycle():
    data = {
        "a": "@format {this.b.foo}",
        "b": {"foo": "@format foo_{this.a}"},
    }
    setting_tree = SettingTree()
    setting_tree.populate(data)
    dependency_graph = pre_evaluate_tree(setting_tree)
    with pytest.raises(CycleError):
        evaluate_tree_dependencies(setting_tree, dependency_graph)
