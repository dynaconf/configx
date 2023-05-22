"""
(Tree)Bucket API behaviour
"""

import pytest

from lib.core.bucket import Bucket
from lib.core.nodes import LeafNode, NodeId, PathNode
from lib.core.nodes import Setting as S


def main():
    root = PathNode("root", None)
    nodeA = LeafNode(S("foo", "content"), root)
    nodeB = LeafNode(S("bar", 123), root)
    nodeC = PathNode("spam", root)
    nodeD = PathNode("eggs", root)

    b = Bucket([nodeA, nodeB, nodeC, nodeD])
    b.inspect(verbose=1)


def test_bucket_initialization():
    """
    Given init with or without init args
    Should succeed
    """
    a = Bucket()
    assert len(a) == 0

    b = Bucket([PathNode("foo", None)])
    assert len(b) == 1

    c = Bucket([PathNode("foo", None), PathNode("bar", None)])
    assert len(c) == 2


def test_bucket_append_node():
    """
    Should append nodes correctly
    """
    b = Bucket()
    root = PathNode("root", None)
    nodeA = PathNode("foo", root)
    nodeB = LeafNode(S("spam", "eggs"), root)

    b.append(nodeA)
    assert len(b) == 1

    b.append(nodeB)
    assert len(b) == 2


def test_bucket_duplicate_handling():
    """
    Should not allow duplicates.
    """
    root = PathNode("root", None)
    nodeA = LeafNode(S("foo", "bar"), root)
    nodeB = LeafNode(S("foo", "value"), root)
    b = Bucket([nodeA, nodeB])
    assert len(b) == 1
    assert b[0].setting.raw_data == "value"


def test_bucket_get_by_props__leaf_nodes():
    """
    Should get leaf node list from given properties
    """
    root = PathNode("root", None)
    nodeA = LeafNode(S("foo", "bar"), root)
    nodeB = LeafNode(S("foo", "bar", env="production"), root)
    nodeC = LeafNode(S("foo", "bar", source="file:/home/settings.toml"), root)
    nodeD = LeafNode(S("spam", "eggs"), root)
    b = Bucket([nodeA, nodeB, nodeC, nodeD])

    nodes = b.get_by_props("foo")
    assert len(nodes) == 3
    assert nodeA == nodes[0]
    assert nodeB == nodes[1]
    assert nodeC == nodes[2]


def test_bucket_get_by_index():
    """
    Should get a single node from index
    """
    nodeA = PathNode("foo", None)
    nodeB = PathNode("bar", None)
    nodeC = PathNode("spam", None)

    b = Bucket([nodeA])
    b.append(nodeB)
    b.append(nodeC)

    assert len(b) == 3
    assert nodeA == b.get_by_index(0)
    assert nodeB == b.get_by_index(1)
    assert nodeC == b.get_by_index(2)


if __name__ == "__main__":
    exit(main())
