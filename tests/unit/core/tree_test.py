"""
Test Tree API behaviour
"""

from typing import Iterable

import pytest

from lib.core.nodes import LeafNode, PathNode, Setting
from lib.core.tree import (
    MultipleNodesFoundError,
    PathNotFoundError,
    Tree,
    get_nodes_by_path_from,
)
from lib.operations.evaluation import evaluate_subtree


def test_get_nodes_by_path_from():
    """
    Should return the correct nodes given a valid TreePath

    *most of these test-assertions rely on this working correctly
    """
    # create raw tree
    root = PathNode("root", None)
    nodeA = LeafNode(Setting("foo", "bar"), root)
    nodeA_diff_env = LeafNode(Setting("foo", "bar", env="prod"), root)
    nodeB = PathNode("nesting_b", root)
    nodeC = PathNode("nesting_c", nodeB)

    root.children.append(nodeA)
    root.children.append(nodeA_diff_env)
    root.children.append(nodeB)
    nodeB.children.append(nodeC)

    nodeD = LeafNode(Setting("nested", 123), nodeC)
    nodeC.children.append(nodeD)

    # same name but different ids (env, in this case)
    assert list(get_nodes_by_path_from(root, ("foo",)))[0] == nodeA  # type: ignore
    assert list(get_nodes_by_path_from(root, ("foo",)))[1] == nodeA_diff_env  # type: ignore

    # nested values
    assert (
        list(get_nodes_by_path_from(root, ("nesting_b", "nesting_c")))[0]  # type: ignore
        == nodeC
    )
    assert (
        list(get_nodes_by_path_from(root, ("nesting_b", "nesting_c", "nested")))[0]  # type: ignore
        == nodeD
    )


def test_get_nodes_by_path():
    """
    Should get values correctly
    """
    t = Tree()
    t.create_node("single", 123)
    t.create_node("repeated", "bar")
    t.create_node("repeated", "other_bar", env="prod")
    t.create_node("nested", ["some", 456])

    # single value
    result_single = t.get_nodes_by_path(("single",))
    assert isinstance(result_single, (list))
    assert result_single[0].value == 123

    # doubled value
    result_single = t.get_nodes_by_path(("repeated",))
    assert isinstance(result_single, (list))
    assert result_single[0].value == "bar"
    assert result_single[1].value == "other_bar"

    # nested value
    result_single = t.get_nodes_by_path(("nested",))
    assert isinstance(result_single, (list))
    assert result_single[0].children[0].value == "some"
    assert result_single[0].children[1].value == 456


def test_get_nodes_by_path__inexistent_path():
    """
    Should return default or raise when no result is found
    """
    t = Tree()
    t.create_node("single", 123)
    t.create_node("repeated", "bar")
    t.create_node("repeated", "other_bar", env="prod")
    t.create_node("nested", ["some", 456])

    # when no-default should raise
    with pytest.raises(PathNotFoundError):
        t.get_nodes_by_path(("non_existent", "path"))

    # when default should return default
    assert t.get_nodes_by_path(("non_existent", "path"), "default") == "default"


def test_get_node_by_path():
    """
    when one element, should return just one element
    when multiple and first=True, should reutrn first element
    when multiple and first=False, should raise
    """
    t = Tree()
    t.create_node("single", 123)
    t.create_node("repeated", "bar")
    t.create_node("repeated", "other_bar", env="prod")
    t.create_node("nested", ["some", 456])

    # when one element, should return just one element
    assert t.get_node_by_path(("single",)).value == 123

    # when multiple and first=True, should reutrn first element
    assert t.get_node_by_path(("repeated",), first=True).value == "bar"

    # when multiple and first=False, should raise
    with pytest.raises(MultipleNodesFoundError):
        t.get_node_by_path(("repeated",))


def test_get_node_by_path__inexistent_path():
    """
    when no-default should raise
    when default should return default
    """
    t = Tree()
    t.create_node("single", 123)
    t.create_node("repeated", "bar")
    t.create_node("repeated", "other_bar", env="prod")
    t.create_node("nested", ["some", 456])

    # when no-default should raise
    with pytest.raises(PathNotFoundError):
        t.get_node_by_path(("non_existent", "path"))

    # when default should return default
    assert t.get_node_by_path(("non_existent", "path"), "default") == "default"


def test_create_node_from_simple_types():
    """
    Should create node from simple types (not dict/list)
    """
    t = Tree()
    nodeA = t.create_node("my_key", "some_value")
    nodeB = t.create_node("my_other_key", 123)

    assert len(t) == 2
    assert t.get_node_by_path(("my_key",)) == nodeA
    assert t.get_node_by_path(("my_other_key",)) == nodeB


def test_create_node_from_list():
    """
    Should create nodes recursively from list
    """
    t = Tree()
    nodeA = t.create_node("my_key", ["one", "two", "tree"])

    assert isinstance(nodeA, PathNode)
    assert len(t) == 4
    assert t.get_node_by_path(("my_key", "0")) == nodeA.children[0]
    assert t.get_node_by_path(("my_key", "1")) == nodeA.children[1]


def test_create_node_from_dict():
    """
    Should create nodes recursively from list
    """
    t = Tree()
    nodeA = t.create_node("my_key", {"hello": "world", "foo": "bar"})

    assert isinstance(nodeA, PathNode)
    assert len(t) == 3
    assert t.get_node_by_path(("my_key", "hello")) == nodeA.children[0]
    assert t.get_node_by_path(("my_key", "foo")) == nodeA.children[1]


def test_create_node_from_compound_types():
    """
    Should create nodes recursively from dict/list
    """
    t = Tree()
    nodeA = t.create_node("my_key_a", {"hello": "world", "foo": ["one", "two"]})
    nodeB = t.create_node("my_key_b", ["spam", {"eggs": "baz", "bim": "bom"}])

    assert isinstance(nodeA, PathNode)
    assert isinstance(nodeB, PathNode)
    assert len(t) == 10
    assert t.get_node_by_path(("my_key_a", "foo")) == nodeA.children[1]
    assert t.get_node_by_path(("my_key_a", "foo", "1")) == nodeA.children[1].children[1]

    assert t.get_node_by_path(("my_key_b", "1")) == nodeB.children[1]
    assert (
        t.get_node_by_path(("my_key_b", "1", "eggs")) == nodeB.children[1].children[0]
    )


def test_remove_node():
    """
    Should remove node and parent links properly
    """
    t = Tree()
    t.create_node("foo", {"old_value": 123})
    target_node = t.get_node_by_path(("foo", "old_value"))
    result = t.remove_node(target_node)

    assert len(t) == 1
    assert result == target_node

    with pytest.raises(PathNotFoundError):
        t.get_node_by_path(("foo", "old_value"))


def test_replace_node():
    """
    Should replace a node with another
    """
    t = Tree()
    t.create_node("foo", {"old_value": 123})
    new_node = LeafNode(Setting("new_value", 456), None)
    replaced_node = t.get_node_by_path(("foo", "old_value"))
    result = t.replace_node(replaced_node, new_node)

    assert result == replaced_node
    assert t.get_node_by_path(("foo", "new_value")) == new_node

    with pytest.raises(PathNotFoundError):
        t.get_node_by_path(("foo", "old_value"))


def main():
    """
    Functional testing + Usage sample
    """
    t = Tree()
    print(">>> # populating tree")
    print(">>> t.create_node(...)")
    data = {"foo": "bar", "spam": {"nested": "one"}}
    t.create_node("foo", "bar")
    t.create_node("baz", ["blabla", "bembem", {"bim": "bom"}])
    t.create_node("simple", 123)
    t.create_node("simple", 456, env="production")
    t.create_node("spam", {"nested": "one"})
    t.create_node("password", "pass123")

    # create two nodes with same path
    spam_node = list(t.get_nodes_by_path(("spam",)))[0]
    t.create_node("nested", "two", spam_node, env="production")  # type: ignore
    t.create_node("nested", {"more_nesting": True}, spam_node, source="toml")  # type: ignore

    # print tree
    print(">>> t.show()")
    t.show()
    print()

    print(">>> # getting nodes")
    print(">>> t.get_nodes_by_path(('spam', 'nested'))")
    path = ("spam", "nested")
    a = t.get_nodes_by_path(path)
    [print(n) for n in a]

    print()
    print(">>> # evaluating node to python objects")
    root = PathNode("root", None)
    print(">>> evaluate_node(LeafNode(Setting('foo', 123), root))")
    ev = evaluate_subtree(LeafNode(Setting("foo", 123), root))
    print(f"{ev=} {type(ev)}")
    print()

    print(">>> evaluate_node(LeafNode(Setting('bar', 'my_value'), root))")
    ev = evaluate_subtree(LeafNode(Setting("bar", "my_value"), root))
    print(f"{ev=} {type(ev)}")
    print()

    print(">>> evaluate_node(LeafNode(Setting('bar', 12.2), root))")
    ev = evaluate_subtree(LeafNode(Setting("bar", 12.2), root))
    print(f"{ev=} {type(ev)}")
    print()

    print(">>> evaluate_node(nested_node)")

    ev = evaluate_subtree(
        t.create_node("nesting", {"foo": "bar", "spam": [1, 2, 3, 4]}, root)
    )
    print(f"{ev=} {type(ev)}")


if __name__ == "__main__":
    exit(main())
