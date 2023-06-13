import pytest

from configx.core.setting_tree import SettingTree
from configx.operations.evaluation.processors import build_context_from_tree


def _pre_evaluate_tree_mock(setting_tree: SettingTree):
    """Writes real values as if it was already pre-evaluated"""
    for node in setting_tree:
        node.element.real_value = node.element.raw_value


def test_build_context_from_tree_no_filter():
    setting_tree = SettingTree()
    setting_tree.populate({"a": "A", "b": {"c": {"d": "D"}}})
    _pre_evaluate_tree_mock(setting_tree)

    context_object = build_context_from_tree(setting_tree)
    assert context_object.a == "A"
    assert context_object.b == {"c": {"d": "D"}}
    assert context_object.b.c.d == "D"
