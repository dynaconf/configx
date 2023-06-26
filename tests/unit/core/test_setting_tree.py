import pytest

from configx.core.setting_tree import Setting, SettingTree
from configx.exceptions import ChildAlreadyExist


def test_populate_simple_types():
    """
    Should create simple types
    """
    st = SettingTree()

    # first assigment
    st.populate({"name": "foo", "age": 123})
    assert len(st) == 2
    assert len(st.root.children) == 2
    assert st.get_setting(("name",))._raw_value == "foo"
    assert ("root", "name") in st._internal_cache

    # override safeguard
    with pytest.raises(ChildAlreadyExist):
        st.populate({"name": 123})

    assert len(st) == 2
    assert len(st.root.children) == 2
    assert st.get_setting(("name",))._raw_value == "foo"


def test_populate_compound_types():
    """
    Should create compound types resursively
    """
    setting_tree = SettingTree()
    data = {
        "dict_type": {"foo": "bar", "spam": ["egg1", "egg2", "egg3"]},
        "list_type": ["a", True, 123],
    }
    setting_tree.populate(data)

    assert len(setting_tree) == 10
    assert setting_tree.get_setting(("dict_type",)).is_leaf is False
    assert setting_tree.get_setting(("dict_type", "foo"))._raw_value == "bar"
    assert setting_tree.get_setting(("dict_type", "spam", 0))._raw_value == "egg1"

    assert setting_tree.get_setting(("list_type",)).is_leaf is False
    assert setting_tree.get_setting(("list_type", 0))._raw_value == "a"
    assert setting_tree.get_setting(("list_type", 1))._raw_value is True
    assert setting_tree.get_setting(("list_type", 2))._raw_value == 123

    # populate different branch
    setting_tree.populate({"hello": "world"})
    assert len(setting_tree) == 11
    assert setting_tree.get_setting(("hello",))._raw_value == "world"

    # override safeguard
    with pytest.raises(ChildAlreadyExist):
        setting_tree.populate({"dict_type": 123})

    # dict|list merge safeguard
    with pytest.raises(ChildAlreadyExist):
        setting_tree.populate({"dict_type": {"dont_merge_this": 123}})


def test_traverse_tree_values():
    setting_tree = SettingTree()
    data = {
        "dict_type": {"foo": "bar", "spam": ["egg1", "egg2", "egg3"]},
        "list_type": ["a", True, 123],
    }
    setting_tree.populate(data)
    tree_traversal = [node.key for node in setting_tree.values()]
    assert len(tree_traversal) == 10
    assert tree_traversal == ["dict_type", "foo", "spam", 0, 1, 2, "list_type", 0, 1, 2]


def test_traverse_tree_keys():
    setting_tree = SettingTree()
    data = {
        "dict_type": {"foo": "bar", "spam": ["egg1", "egg2", "egg3"]},
        "list_type": ["a", True, 123],
    }
    setting_tree.populate(data)
    tree_traversal = [tree_path for tree_path in setting_tree.keys()]
    assert len(tree_traversal) == 10
    assert tree_traversal == [
        ("root", "dict_type"),
        ("root", "dict_type", "foo"),
        ("root", "dict_type", "spam"),
        ("root", "dict_type", "spam", 0),
        ("root", "dict_type", "spam", 1),
        ("root", "dict_type", "spam", 2),
        ("root", "list_type"),
        ("root", "list_type", 0),
        ("root", "list_type", 1),
        ("root", "list_type", 2),
    ]


def test_traverse_tree_items():
    setting_tree = SettingTree()
    data = {
        "dict_type": {"foo": "bar", "spam": ["egg1", "egg2", "egg3"]},
        "list_type": ["a", True, 123],
    }
    setting_tree.populate(data)
    tree_traversal = [
        (tree_path, node.element._raw_value) for tree_path, node in setting_tree.items()
    ]
    assert len(tree_traversal) == 10
    assert tree_traversal == [
        (("root", "dict_type"), {}),
        (("root", "dict_type", "foo"), "bar"),
        (("root", "dict_type", "spam"), []),
        (("root", "dict_type", "spam", 0), "egg1"),
        (("root", "dict_type", "spam", 1), "egg2"),
        (("root", "dict_type", "spam", 2), "egg3"),
        (("root", "list_type"), []),
        (("root", "list_type", 0), "a"),
        (("root", "list_type", 1), True),
        (("root", "list_type", 2), 123),
    ]
