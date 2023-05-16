from lib.core.setting_tree import SettingTree, Setting


def test_create_setting():
    st = SettingTree()
    n1 = st.create_setting(("foo", "bar", "spam"), "eggs")
    n2 = st.create_setting(("foo", "bar", "number"), 123)

    assert st._get_node(("foo", "bar", "spam")) is n1
    assert st._get_node(("foo", "bar", "number")) is n2

    # assert non-leaf Setting have the corresponding Node as it's raw_value
    foo_node = st._get_node(("foo",))
    assert foo_node.element.raw_value == foo_node


def test_add_setting_with_setting_object():
    st = SettingTree()
    n1 = st.add_setting(Setting(("foo", "bar", "spam"), "eggs"))
    n2 = st.add_setting(Setting(("foo", "bar", "number"), 123))

    assert st._get_node(("foo", "bar", "spam")) is n1
    assert st._get_node(("foo", "bar", "number")) is n2

    # assert non-leaf Setting have the corresponding Node as it's raw_value
    foo_node = st._get_node(("foo",))
    assert foo_node.element.raw_value == foo_node


def test_create_setting_with_compound_types():
    st = SettingTree()
    n1 = st.create_setting(("foo", "bar", "spam"), ["a", "b", "c"])
    n2 = st.create_setting(("foo", "bar", "number"), 123)

    assert st._get_node(("foo", "bar", "spam")) is n1
    assert st._get_node(("foo", "bar", "number")) is n2


def test_load_dict():
    pass
