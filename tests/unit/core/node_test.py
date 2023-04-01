"""
PathNode and LeafNode API behaviour and representation
"""

import pytest

from lib.core.nodes import BaseNode, LeafNode, PathNode
from lib.core.nodes import Setting as S

# from tests.utils import print_header


def main():
    """
    Functional test of general API usage
    """
    # create raw Tree structure
    root = PathNode("root", None)
    node_a = LeafNode(
        S("some_key", "value"),
        root,
    )
    node_c = PathNode("dict_object", root)
    node_b = LeafNode(
        S("some_other_key", 12),
        node_c,
    )
    node_c.children.append(node_b)

    print_header("printing/inspecting")
    # printing
    nodes: list[BaseNode] = [root, node_a, node_b]
    for n in nodes:
        print()
        print("> " + str(n))
        print(f"\t{n.get_full_path()}")

    print_header("Path-Node identity")
    # path node identity
    nodeA = PathNode("test_value", root)
    nodeB = PathNode("test_value", root)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")
    print()

    nodeA = PathNode("test_value", root)
    nodeB = PathNode("test_value", nodeA)
    nodeA.children.append(nodeB)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")

    print_header("Leaf-Node identity")
    # leaf node identity
    nodeA = LeafNode(S("test_value", "foo"), root)
    nodeB = LeafNode(S("test_value", "foo"), root)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")
    print()

    nodeA = LeafNode(S("test_value", "foo"), root)
    nodeB = LeafNode(S("test_value", "foo"), nodeA)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")
    print()

    nodeA = LeafNode(S("test_value", "foo"), root)
    nodeB = LeafNode(S("test_value", "bar"), root)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")
    print()

    nodeA = LeafNode(S("test_value", "foo"), root)
    nodeB = LeafNode(S("test_value", "foo", env="production"), root)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")
    print()

    nodeA = LeafNode(S("test_value", "foo"), root)
    nodeB = LeafNode(S("test_value", "foo", source="file:/tmp/settings.toml"), root)
    is_nodeAB = nodeA == nodeB
    print(nodeA.inspect())
    print(nodeB.inspect())
    print(f"nodeA == nodeB: {is_nodeAB}")

    return 0


################
# UNIT TESTING #
################


def test_trivial():
    ...


###############
# END TESTING #
###############


def print_header(text: str):
    """
    prints header in this formmat:
    ========
    = text =
    ========
    """
    mult = len(text) + 4
    print()
    print("=" * mult)
    print(f"= {text.upper()} =")
    print("=" * mult)


def main_wrapper():
    """
    Wrapper for testing function
    """
    try:
        return main()
    except Exception as e:
        return e


def test_main():
    assert main_wrapper() == 0


if __name__ == "__main__":
    exit(main())
