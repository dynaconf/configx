"""
General sandbox file
"""

from dataclasses import dataclass
from typing import Any, reveal_type

import pytest

from lib.core.tree import BaseNode
from lib.core.tree import Bucket as B
from lib.core.tree import LeafNode
from lib.core.tree import Node as N
from lib.core.tree import PathNode
from lib.core.tree import Setting as S
from lib.core.tree import Tree as T
from lib.shared.types import TreePath
from lib.shared.utils import normalize_compound_type




def test_BaseNode():
    root = BaseNode(name="root")
    node_a = BaseNode(root, "a")
    node_b = BaseNode(root, "b")
    node_c = BaseNode(node_a, "c")
    node_d = BaseNode(node_a, "d")
    node_e = BaseNode(node_c, "e")
    nodes = [root, node_a, node_b, node_c, node_d, node_e]

    # full path
    for n in nodes:
        print(n.show_path())


def stash_bucket_inspect():
    nodeA = N("foo")
    nodeB = N("bar")
    nodeC = N("spam", S("spam", "eggs"))
    nodeD = N("nested", parent=nodeA)
    nodeA.children.append(nodeD)

    b = B([nodeA, nodeB, nodeC, nodeD])
    b.inspect(verbose=True, relative_path=False)


def test_create_and_get_nodes():
    t = T()
    t.create_node("node", "this_is_a_string")
    t.create_node("foo", 1)
    t.create_node("compound", ["foo", "bar", {"level": 4}])
    t.show()
    a = t.get_nodes_by_path(("foo",))
    print(a)
    # t.show()


def test_normalize_compound_type():
    # list should convert
    c = [1, "spam", {"foo": "bar"}]
    normalized = normalize_compound_type(c)
    assert normalized[0] == 1
    assert normalized[1] == "spam"
    assert normalized[2] == {"foo": "bar"}

    # dict should bypass
    d = {"name": "John", "age": 34, "items": [1, 2, 3, 4]}
    normalized_bypass = normalize_compound_type(d)
    assert normalized_bypass["name"] == "John"
    assert normalized_bypass["age"] == 34
    assert normalized_bypass["items"] == [1, 2, 3, 4]


if __name__ == "__main__":
    exit(main())
