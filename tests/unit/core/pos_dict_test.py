import pytest

from lib.core.bucket import PositionalDict
from lib.core.nodes import BaseNode, LeafNode, NodeId, PathNode
from lib.core.nodes import Setting as S

params__positional_dict__initial = (
    pytest.param([("foo", 1)], id="one-element"),
    pytest.param([("foo", 1), ("bar", 2), ("baz", 3)], id="multiple-element"),
)


@pytest.mark.parametrize("initial", params__positional_dict__initial)
def test_pos_dict_init(initial):
    """
    Given initialization arguments
    Should succeed
    TODO should this be parametrized?
    """
    p = PositionalDict(initial)

    assert len(p) == len(initial)
    for i, value in enumerate(initial):
        k, v = value
        assert p[k] == v
        assert p[i] == v


def test_pos_dict_init__repeated_elements():
    """
    Should not allow repeated elements (kinda trivial)
    """
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
    node = PathNode("foo", None)
    p = PositionalDict()
    p[node.identifier] = node

    assert len(p) == 1
    assert p[0] == node


def test_pos_dict_get_node_by_index():
    """
    Should return Node by it's index
    """
    nodeA = PathNode("foo", None)
    nodeB = PathNode("bar", None)
    nodeC = PathNode("spam", None)
    p = PositionalDict([(nodeA, nodeA)])
    p.update({nodeB: nodeB, nodeC: nodeC})
    assert p[0] == nodeA
    assert p[1] == nodeB
    assert p[2] == nodeC


def test_pos_dict_get_node_by_id():
    """
    Should return Node by it's identity.
    """
    root = PathNode("root", None)
    nodeA = PathNode("foo", None)
    nodeB = LeafNode(S("bar", "value", "env", "src"), root)
    nodeC = PathNode("spam", None)

    p = PositionalDict()
    p.update(
        {nodeA.identifier: nodeA, nodeB.identifier: nodeB, nodeC.identifier: nodeC}
    )

    # PathNode
    id_queryA = NodeId(("foo",))
    assert p[nodeA.identifier] == nodeA
    assert p[id_queryA] == nodeA

    # LeafNode
    id_queryB = NodeId(("root", "bar"), "env", "src")
    assert p[nodeB.identifier] == nodeB
    assert p[id_queryB] == nodeB
