from __future__ import annotations

from dataclasses import dataclass, field
from sys import exception
from typing import Any

from lib.shared.types import AllTypes, CompoundTypes, SimpleTypes, TreePath
from lib.shared.utils import normalize_compound_type


def main():
    st = SettingTree()
    st.add_setting(Setting(("foo", "bar", "spam"), "eggs"))
    st.show_map()
    print(st.get_setting(("foo", "bar", "spam")))


### Tree


@dataclass
class Setting:
    path: TreePath
    raw_value: SimpleTypes | CompoundTypes
    real_value: Any = None

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
        path = to_tree_path(child)
        result = [n for n in self.children if n.path == path]
        if result:
            return result[0]

        if default is None:
            raise NodeNotFound(f"Child is not found in node: {self}")
        return default

    def find_child(self, child: Node | TreePath, default: Node | None = None) -> Node:
        """
        Find child resursively
        """
        path = to_tree_path(child)
        ...

    def child_exist(self, child: Node | TreePath) -> bool:
        try:
            self.get_child(child)
            return True
        except NodeNotFound:
            return False

    def add_child(self, child: Node, overwrite=True):
        """
        Adds child to node.
        """
        if self.child_exist(child):
            raise ChildAlreadyExist(f"Child already exist: {repr(child.name)}")
        self._children.append(child)

    @property
    def is_leaf(self) -> bool:
        return self.element.is_leaf

    @property
    def path(self):
        return self.element.path

    @property
    def name(self):
        """Printable name"""
        return ".".join([str(v) for v in self.element.path])

    @property
    def children(self):
        return self._children

    def __repr__(self):
        return "Node({}, child_count={})".format(
            repr(self.element),
            len(self.children),
        )


def to_tree_path(path_or_node: TreePath | Node) -> TreePath:
    """
    Convenience: gets TreePath from node or bypasses if already TreePath
    """
    n = path_or_node
    return n if isinstance(n, tuple) else n.path


class SettingNotFound(Exception):
    pass


class NodeNotFound(Exception):
    pass


class EmptyTreePath(Exception):
    pass


class ChildAlreadyExist(Exception):
    pass


class EMTPY:
    pass


TreeMap = dict[TreePath, Node]


class SettingTree:
    def __init__(self, env: str = "default", src: str = "memory"):
        self.root = Node(Setting(("root",), ""), None)  # type: ignore
        self.root.parent = self.root
        # TODO: add optional populate on init: ST( dict | Node, ... )

        # TODO: setup cache system (can be posponed)
        self._internal_cache: TreeMap = {self.root.path: self.root}
        self._user_cache: dict[TreePath, dict[str, AllTypes]] | None = None

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
            n = Node(Setting(path, raw_value), parent)
            parent.add_child(n)
            self._internal_cache[n.path] = n
            return n

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

        s = Setting(path, non_leaf_sentinel)
        n = Node(s, parent)
        parent.add_child(n)
        self._internal_cache[n.path] = n

        for k, v in non_leaf_iterator(raw_value):
            new_path = path + (k,)
            self._populate(new_path, v, n)
        return n

    def create_node(
        self,
        key: str | int,
        raw_value: SimpleTypes | CompoundTypes,
        parent: Node | None = None,
    ) -> Node:
        """Create and add node to key"""
        ...

    def replace_node(self, new_setting: Setting, node_path: TreePath) -> Node:
        ...

    def remove_node(self, new_setting: Setting, node_path: TreePath) -> Node:
        ...

    def get_setting(self, path: TreePath) -> Setting:
        return self._get_node(path).element

    def node_exist(self, path: TreePath) -> bool:
        try:
            self._get_node(path)
            return True
        except NodeNotFound:
            return False

    def _get_node(self, rootless_path: TreePath, default: Node | None = None) -> Node:
        if len(rootless_path) == 0:
            raise EmptyTreePath

        rooted_path = self.root.path + rootless_path
        try:
            return self._internal_cache[rooted_path]
        except KeyError:
            if default is None:
                raise NodeNotFound(f"Node not found for path: {rooted_path}")
            return default

    # def _get_parent_from_tree_path(self, path: TreePath) -> Node:
    #     try:
    #         parent = self._get_node(path[:-1])
    #     except SettingNotFound:
    #         parent = self._add_setting(Setting(path[:-1], "", is_leaf=False))
    #         parent.element.raw_value = parent
    #     except EmptyTreePath:
    #         parent = self.root
    #     return parent

    def _setting_exist(self, setting_path: TreePath) -> bool:
        return setting_path in self._internal_cache

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

    def __len__(self):
        return len(self._internal_cache) - 1


if __name__ == "__main__":
    exit(main())
