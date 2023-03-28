"""
(Tree)Bucket API behaviour
"""

import pytest

from lib.core.tree import Bucket as B
from lib.core.tree import Node as N
from lib.core.tree import Setting as S


def test_bucket_initialization():
    """
    Given init with or without init args
    Should succeed
    """
    a = B()
    assert len(a) == 0

    b = B([N("foo")])
    assert len(b) == 1

    c = B([N("foo"), N("bar", None)])
    assert len(c) == 2


def test_bucket_append_node():
    """
    Should append nodes correctly
    """
    b = B()
    b.append(N("foo"))
    assert len(b) == 1

    b.append(N("bar"))
    assert len(b) == 2


def test_bucket_duplicate_handling():
    """
    Should not allow duplicates.

    The identify should be defined as
    - PathNode: (path)
    - LeafNode: (path, env, source)

    Either by hash or by relative_id_str
    """
    nodeA = N("foo", S("foo", "bar"))
    nodeB = N("foo", S("foo", "bar"))
    nodeC = N("foo", S("foo", "bar"))
    b = B([nodeA, nodeB, nodeC])


def test_bucket_get_by_props__leaf_nodes():
    """
    Should get leaf node list from given properties
    """
    nodeA = N("foo", S("foo", "bar"))
    nodeB = N("foo", S("foo", "bar"))
    nodeC = N("foo", S("foo", "bar"))
    b = B([nodeA, nodeB, nodeC])

    assert nodeA == b.get_by_props("foo")[0]
    assert nodeB == b.get_by_props("foo")[1]
    assert nodeC == b.get_by_props("foo")[2]


def test_bucket_get_by_index():
    """
    Should get a single node from index
    """
    nodeA = N("foo")
    nodeB = N("bar")
    nodeC = N("spam")

    b = B([nodeA])
    assert nodeA == b.get_by_index(0)

    b.append(nodeB)
    b.append(nodeC)

    assert nodeB == b.get_by_index(1)
    assert nodeC == b.get_by_index(2)
    assert len(b) == 3
