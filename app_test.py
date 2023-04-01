"""
General sandbox file
"""

from dataclasses import dataclass
from typing import Any, reveal_type

import pytest

from lib.core.bucket import Bucket
from lib.core.nodes import BaseNode, LeafNode, NodeId, PathNode
from lib.core.nodes import Setting as S
from lib.core.tree import Tree as T
from lib.shared.types import TreePath
from lib.shared.utils import normalize_compound_type


def main():
    root = PathNode("root", None)
    n = LeafNode(S("foo", "bar", "env", "src"), root)

    print(hash(n))
    print(hash(NodeId(("root", "foo"), "env", "src")))


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
