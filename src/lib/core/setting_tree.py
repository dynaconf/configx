from __future__ import annotations
from dataclasses import dataclass, field
from lib.shared.types import SimpleTypes, TreePath
from typing import Any


def main():
    st = SettingTree()
    st.add_setting(Setting(("foo", "bar", "spam"), "eggs"))
    st.show_map()
    print(st.get_setting(("foo", "bar", "spam")))


### Tree


@dataclass
class Setting:
    path: TreePath
    raw_value: SimpleTypes | Node
    real_value: Any = None
    is_leaf: bool = True

    @property
    def _is_leaf(self):
        return isinstance(self.raw_value, Node)


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
        if not result:
            raise NodeNotFound(f"Child is not found in node: {self}")
        return result[0]

    def find_child(self, child: Node | TreePath, default: Node | None = None) -> Node:
        """
        Find child resursively
        """
        path = to_tree_path(child)
        ...

    def add_child(self, child: Node, overwrite=True):
        """
        Adds child to node.
        """

    @property
    def path(self):
        return self.element.path

    @property
    def children(self):
        return self._children

    def __repr__(self):
        return "Node(parent={}, child_count={}, setting={})".format(
            repr(self.parent.element.path[-1]),
            len(self.children),
            repr(self.element),
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


class EMTPY:
    pass


TreeMap = dict[TreePath, Node]


class SettingTree:
    def __init__(self, env: str = "default", src: str = "memory"):
        self.root = Node(Setting(("root",), ""), None)  # type: ignore
        self.root.parent = self.root
        self.tree_map: TreeMap = {self.root.path: self.root}
        self.env = env
        self.src = src

    def load_dict(self, data: dict):
        """
        Load dictonary as Setting instances to Tree
        """
        ...

    def create_setting(self, path: TreePath, raw_value: SimpleTypes) -> Node:
        """
        Create and add setting using @path and @raw_value
        """
        return self.add_setting(Setting(path, raw_value))

    def add_setting(self, setting: Setting) -> Node:
        """
        Add @setting and creates intermediary settings if necessary.
        Returns created node
        """
        path = setting.path
        new_node = self._add_setting(setting)

        # create non-leaf setting, if does not exit yet
        for i in range(1, len(path)):
            if not self.setting_exist(path[:i]):
                n = self._add_setting(Setting(path[:i], "", is_leaf=False))
        return new_node

    def _add_setting(self, setting: Setting) -> Node:
        """
        Add a single setting using setting path definition
        """
        path = setting.path
        try:
            parent = self._get_node(path[:-1])
        except SettingNotFound:
            parent = self._add_setting(Setting(path[:-1], "", is_leaf=False))
            parent.element.raw_value = parent
        except EmptyTreePath:
            parent = self.root

        new_node = Node(setting, parent)
        if path not in self.tree_map:
            parent.children.append(new_node)
        self.tree_map[new_node.path] = new_node
        return new_node

    # def replace_node(self, new_setting: Setting, node_path: TreePath) -> Node:
    #     node = self.get_node(node_path)
    #     node.element = new_setting
    #     return node

    def remove_setting(self, path: TreePath) -> Node:
        node = self._get_node(path)
        node.parent.children.remove(node)
        del self.tree_map[path]
        return node

    def get_setting(self, path: TreePath, default: Node | None = None) -> Setting:
        node = self._get_node(path, default)
        return node.element

    def _get_node(self, path: TreePath, default: Node | None = None) -> Node:
        if len(path) == 0:
            raise EmptyTreePath
        try:
            return self.tree_map[path]
        except KeyError:
            if default is None:
                raise SettingNotFound(f"Setting not found for path: {path}")
            return default

    def setting_exist(self, setting_path: TreePath) -> bool:
        try:
            self.get_setting(setting_path)
            return True
        except SettingNotFound:
            return False

    def show_map(self):
        for k, v in self.tree_map.items():
            print(k, v.element)

    def show_tree(self, debug: bool = False):
        self._show_tree(self.root, debug=debug)

    def _show_tree(self, node: Node, depth: int = 0, debug=False):
        spacing = "  " * depth
        setting_name = node.element.path[-1]
        setting_value = node.element.raw_value if not debug else node
        print("{}{}: {}".format(spacing, setting_name, setting_value))
        for n in node.children:
            self._show_tree(n, depth + 1, debug)

    def __len__(self):
        return len(self.tree_map)


if __name__ == "__main__":
    exit(main())
