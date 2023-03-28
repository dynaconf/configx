import pytest

from lib.core.tree import Node as N
from lib.core.tree import PositionalDict

params__positional_dict__initial = (
    pytest.param([("foo", 1)], id="one-element"),
    pytest.param([("foo", 1), ("bar", 2), ("baz", 3)], id="multiple-element"),
)


@pytest.mark.parametrize("initial", params__positional_dict__initial)
def test_pos_dict_init(initial):
    """
    Given initialization arguments
    Should succeed
    """
    p = PositionalDict(initial)

    assert len(p) == len(initial)
    for i, value in enumerate(initial):
        k, v = value
        assert p[k] == v
        assert p[i] == v


def test_pos_dict_init__repeated_elements():
    # on init
    p_init = PositionalDict([("foo", "A"), ("foo", "B")])
    assert len(p_init) == 1
    assert p_init["foo"] == "B"

    # one by one
    p_setting = PositionalDict()
    p_setting["foo"] = "A"
    p_setting["foo"] = "B"
    assert len(p_setting) == 1
    assert p_setting["foo"] == "B"


def test_pos_dict_set():
    p = PositionalDict()
    p["foo"] = "bar"

    assert len(p) == 1
    assert p["foo"] == "bar"


def test_pos_dict_set__node():
    node = N("foo")
    p = PositionalDict()
    p[node] = node

    assert len(p) == 1
    assert p[0] == node

def test_pos_dict_get_by_index__node():
    """
    Should return Node by it's index
    """
    node = N("foo")
    p = PositionalDict([(node, node)])
    assert p[0] == node

def test_pos_dict_get_by_name__node():
    """
    Should return Node by it's identify.
    In case of node, it can be (name) or (name, env, source)

    not sure if this is needed
    """
