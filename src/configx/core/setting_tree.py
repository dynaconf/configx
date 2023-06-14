"""
Holds the core data structure to hold and provide
essential operations over Setting objects consistently.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Any

from configx.exceptions import ChildAlreadyExist, EmptyTreePath, NodeNotFound
from configx.types import (
    MISSING,
    NOT_EVALUATED,
    CompoundTypes,
    LazyValue,
    PrimitiveTypes,
    SimpleTypes,
    TreeMap,
    TreePath,
)
from configx.utils.general_utils import print_header
from configx.utils.tree_utils import assure_tree_path


def main():
    """Usage samples"""
    data = {
        "a": "A",
        "listy": [1, 2, {"b": [3, 4]}],
        "dicty": {"c": "C", "d": [5, 6, {"e": "E"}]},
    }
    setting_tree = SettingTree()
    setting_tree.populate(data)

    print_header("show_tree")
    setting_tree.show_tree()

    print_header("show_map")
    setting_tree.show_map()

    print_header("print(get_setting)")
    print(setting_tree.get_setting(("a",)))
    print(setting_tree.get_setting(("listy", 2, "b", 1)))
    print(setting_tree.get_setting(("dicty", "d", 2, "e")))

    print_header("for node in setting_tree (iteration)")
    for node in setting_tree:
        print(node.dot_path, node.element.raw_value)


@dataclass
class Setting:
    path: TreePath
    raw_value: PrimitiveTypes | LazyValue
    real_value: Any = NOT_EVALUATED

    @property
    def is_leaf(self):
        return isinstance(type(self.raw_value), CompoundTypes)


@dataclass
class Node:
    element: Setting
    parent: Node
    _children: list[Node] = field(default_factory=list)

    def get_child(self, child: Node | TreePath, default: Node | None = None) -> Node:
        """
        Get immediate child of self (not recursive)
        """
        path = assure_tree_path(child)
        result = [n for n in self.children if n.path == path]
        if result:
            return result[0]

        if default is None:
            raise NodeNotFound(f"Child is not found in node: {self}")
        return default

    def add_child(self, child: Node, overwrite=True):
        """
        Adds child to node.
        """
        if self.child_exist(child):
            raise ChildAlreadyExist(f"Child already exist: {repr(child.dot_path)}")
        self._children.append(child)

    def remove_child(self, child: Node | TreePath):
        """Removes child by Node identity or TreePath"""
        ...

    def child_exist(self, child: Node | TreePath) -> bool:
        try:
            self.get_child(child)
            return True
        except NodeNotFound:
            return False

    @property
    def children(self):
        return self._children

    # convenience properties

    @property
    def is_leaf(self) -> bool:
        return self.element.is_leaf

    @property
    def is_evaluated(self) -> bool:
        return self.element.real_value is not NOT_EVALUATED

    @property
    def is_pre_evaluated(self) -> bool:
        return isinstance(self.element.raw_value, LazyValue)

    @property
    def path(self):
        """Get Node's TreePath"""
        return self.element.path

    @property
    def dot_path(self):
        """Get Node's dot path string"""
        return ".".join([str(v) for v in self.element.path])

    @property
    def key(self):
        """Get Node's key (last name from full Node path)"""
        return self.element.path[-1]

    @property
    def value(self):
        """Get Node's value (raise if not evaluated)"""
        if not self.is_evaluated:
            raise ValueError("Node value is not evaluated yet")
        return self.element.real_value

    def __repr__(self):
        return "Node({}, child_count={})".format(
            repr(self.element),
            len(self.children),
        )


class SettingTree:
    def __init__(self, env: str = "default", src: str = "memory"):
        # TODO: add optional populate on init: ST( dict | Node, ... )
        # TODO: setup cache system (can be posponed)
        self.root = Node(Setting(("root",), ""), None)  # type: ignore
        self.root.parent = self.root
        self._internal_cache: TreeMap = {self.root.path: self.root}

        self.env = env
        self.src = src

    def populate(
        self,
        py_data: dict[str, SimpleTypes | CompoundTypes],
        basenode: Node | None = None,
    ):
        """
        Create Nodes recursively from data structured as dict.
        Used for fresh populate and does not support merging.

        Example:
            >>> data = {"foo": "bar", "compound": ["a", True, 123]}
            >>> st = SettingTree(data)
            >>> st.show_tree()
            "root":
                "foo": "bar"
                "compound":
                    0: "a"
                    1: True
                    2: 123
        """
        # get parent where nodes will be appended
        basenode = basenode or self.root
        rooted_path = basenode.path

        # use py_data [key, values] as Setting(path, raw_value)
        for k, v in py_data.items():
            new_path = rooted_path + (k,)
            self._populate(new_path, v, basenode)
        return basenode

    def _populate(
        self, path: TreePath, raw_value: SimpleTypes | CompoundTypes, parent: Node
    ):
        """
        Resursively create Node/Setting from python objects
        """
        # basecase: leaf-node
        if isinstance(raw_value, SimpleTypes):
            node = Node(Setting(path, raw_value), parent)
            parent.add_child(node)
            self._internal_cache[node.path] = node
            return node

        # general case: non-leaf node
        # TODO: use list and dict sentinels {DICT, LIST} -> type(LIST)=list
        if isinstance(raw_value, list):
            non_leaf_sentinel = []
            non_leaf_iterator = lambda x: enumerate(x)
        elif isinstance(raw_value, dict):
            non_leaf_sentinel = {}
            non_leaf_iterator = lambda x: x.items()
        else:
            raise TypeError("`py_data` should be list or dict")

        setting = Setting(path, non_leaf_sentinel)
        node = Node(setting, parent)
        parent.add_child(node)
        self._internal_cache[node.path] = node

        for k, v in non_leaf_iterator(raw_value):
            new_path = path + (k,)
            self._populate(new_path, v, node)
        return node

    def create_node(
        self,
        key: str | int,
        raw_value: SimpleTypes | CompoundTypes,
        parent: Node = MISSING,
    ) -> Node:
        """Create and add node to key"""
        ...

    def replace_node(self, new_setting: Setting, node_path: TreePath) -> Node:
        ...

    def remove_node(self, new_setting: Setting, node_path: TreePath) -> Node:
        ...

    def get_node(self, rootless_path: TreePath, default: Node | None = None) -> Node:
        if len(rootless_path) == 0:
            raise EmptyTreePath

        rooted_path = self.root.path + rootless_path
        try:
            return self._internal_cache[rooted_path]
        except KeyError:
            if default is None:
                raise NodeNotFound(f"Node not found for path: {rooted_path}")
            return default

    def get_setting(self, path: TreePath) -> Setting:
        """Convenient method to get Setting of node"""
        return self.get_node(path).element

    def node_exist(self, path: TreePath) -> bool:
        try:
            self.get_node(path)
            return True
        except NodeNotFound:
            return False

    def _setting_exist(self, setting_path: TreePath) -> bool:
        return setting_path in self._internal_cache

    # traversal

    def _pre_order(self, node: Node):
        yield node
        for child in node.children:
            for other in self._pre_order(child):
                yield other

    def values(self, use_cache: bool = False):
        """Yields Node (exclude root)"""
        iterable = self._pre_order(self.root)
        yield from itertools.islice(iterable, 1, None)

    def keys(self, use_cache: bool = False):
        """Yields TreePath (exlude root)"""
        iterable = self._pre_order(self.root)
        iterable = itertools.islice(iterable, 1, None)
        yield from (it.path for it in iterable)

    def items(self, use_cache: bool = False):
        """Yields (TreePath, Node) (exlude root)"""
        iterable = self._pre_order(self.root)
        iterable = itertools.islice(iterable, 1, None)
        yield from ((it.path, it) for it in iterable)

    # display

    def show_map(self):
        for k, v in self._internal_cache.items():
            print(k, v.element)

    def show_tree(self, debug: bool = False):
        """Print formatted tree representation"""
        self._show_tree(self.root, debug=debug)

    def _show_tree(self, node: Node, depth: int = 0, debug=False):
        """
        Recursively prints tree nodes
        """
        spacing = "  " * depth
        setting_name = repr(node.element.path[-1])
        setting_value = repr(node.element.raw_value) if not debug else node
        print("{}{}: {}".format(spacing, setting_name, setting_value))
        for n in node.children:
            self._show_tree(n, depth + 1, debug)

    # dunder

    def __iter__(self):
        """Pre-order iteration"""
        yield from self.values()

    def __len__(self):
        return len(self._internal_cache) - 1


if __name__ == "__main__":
    exit(main())