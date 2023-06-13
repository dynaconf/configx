import pytest

from configx.core.setting_tree import Setting, SettingTree
from configx.exceptions import ChildAlreadyExist

# def test_create_setting():
#     st = SettingTree()
#     n1 = st.create_node(("foo", "bar", "spam"), "eggs")
#     n2 = st.create_node(("foo", "bar", "number"), 123)

#     assert st._get_node(("foo", "bar", "spam")) is n1
#     assert st._get_node(("foo", "bar", "number")) is n2

#     # assert non-leaf Setting have the corresponding Node as it's raw_value
#     foo_node = st._get_node(("foo",))
#     assert foo_node.element.raw_value == foo_node


# def test_add_setting_with_setting_object():
#     st = SettingTree()
#     n1 = st.add_setting(Setting(("foo", "bar", "spam"), "eggs"))
#     n2 = st.add_setting(Setting(("foo", "bar", "number"), 123))

#     assert st._get_node(("foo", "bar", "spam")) is n1
#     assert st._get_node(("foo", "bar", "number")) is n2

#     # assert non-leaf Setting have the corresponding Node as it's raw_value
#     foo_node = st._get_node(("foo",))
#     assert foo_node.element.raw_value == foo_node


# def test_create_setting_with_compound_types():
#     st = SettingTree()
#     n1 = st.create_node(("foo", "bar", "spam"), ["a", "b", "c"])
#     n2 = st.create_node(("foo", "bar", "number"), 123)

#     assert st._get_node(("foo", "bar", "spam")) is n1
#     assert st._get_node(("foo", "bar", "number")) is n2


# def test_load_dict():
#     pass


def test_populate_simple_types():
    """
    Should create simple types
    """
    st = SettingTree()

    # regular assigment
    st.populate({"name": "foo", "age": 123})
    assert len(st) == 2
    assert len(st.root.children) == 2
    assert st.get_setting(("name",)).raw_value == "foo"
    assert ("root", "name") in st._internal_cache

    # override safeguard
    with pytest.raises(ChildAlreadyExist):
        st.populate({"name": 123})

    assert len(st) == 2
    assert len(st.root.children) == 2
    assert st.get_setting(("name",)).raw_value == "foo"


def test_populate_compound_types():
    """
    Should create compound types resursively
    """
    st = SettingTree()

    # Regular assignment
    data = {
        "dict_type": {"foo": "bar", "spam": ["egg1", "egg2", "egg3"]},
        "list_type": ["a", True, 123],
    }
    st.populate(data)

    assert len(st) == 10
    assert st.get_setting(("dict_type",)).is_leaf is False
    assert st.get_setting(("dict_type", "foo")).raw_value == "bar"
    assert st.get_setting(("dict_type", "spam", 0)).raw_value == "egg1"

    assert st.get_setting(("list_type",)).is_leaf is False
    assert st.get_setting(("list_type", 0)).raw_value == "a"
    assert st.get_setting(("list_type", 1)).raw_value is True
    assert st.get_setting(("list_type", 2)).raw_value == 123

    # populate different branch
    st.populate({"hello": "world"})
    assert len(st) == 11
    assert st.get_setting(("hello",)).raw_value == "world"

    # override safeguard
    with pytest.raises(ChildAlreadyExist):
        st.populate({"dict_type": 123})

    # dict|list merge safeguard
    with pytest.raises(ChildAlreadyExist):
        st.populate({"dict_type": {"dont_merge_this": 123}})
