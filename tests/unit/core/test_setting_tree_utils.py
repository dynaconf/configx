import pytest

from configx.core.setting_tree import SettingTree
from configx.utils.tree_utils import str_to_tree_path
from configx.utils.tree_utils import tree_to_dict


def test_str_to_tree_path():
    """
    When string has a valid dot path format
    Should convert to a TreePath
    """
    assert str_to_tree_path("foo") == ("foo",)
    assert str_to_tree_path("foo.bar") == ("foo", "bar")
    assert str_to_tree_path(".foo.bar") == ("", "foo", "bar")


def test_tree_to_dict_flat():
    """
    When
        tree has one level
        tree has only raw types (bypass @tokens)
    Should return the correct python data structure
    """
    data = {"a": "A", "b": "B"}
    setting_tree = SettingTree()
    setting_tree.create_node("str_node", "value")
    setting_tree.create_node("int_node", 123)
    setting_tree.create_node("float_node", 1.23)

    result = tree_to_dict(setting_tree.root)
    assert isinstance(result, dict)
    assert result["str_node"] == "value"
    assert result["int_node"] == 123
    assert result["float_node"] == 1.23


def test_tree_to_dict_nested():
    """
    When
        tree has multiple levels
        tree has only raw types
    Should return the correct python data structure
    """
    t = SettingTree()
    t.create_node(
        "nesting_a",
        {
            "str_node": "value",
            "int_node": 123,
            "float_node": 1.23,
            "list_node": ["a", "b", "c"],
        },
    )
    t.create_node("nesting_b", [1, 2, 3, {"foo": "bar"}])

    result = tree_to_dict(t.root)
    assert isinstance(result, dict)
    assert result["nesting_a"]["str_node"] == "value"
    assert result["nesting_a"]["int_node"] == 123
    assert result["nesting_a"]["float_node"] == 1.23
    assert result["nesting_a"]["list_node"] == ["a", "b", "c"]
    assert result["nesting_b"][0] == 1
    assert result["nesting_b"][1] == 2
    assert result["nesting_b"][2] == 3
    assert result["nesting_b"][3] == {"foo": "bar"}
