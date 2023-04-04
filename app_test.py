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


if __name__ == "__main__":
    exit(main())
