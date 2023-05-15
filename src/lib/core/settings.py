from __future__ import annotations
from dataclasses import dataclass, field
from lib.shared.types import TreePath
from typing import Any


def main():
    st = SettingTree()
    st.add_setting(Setting(("foo", "bar", "spam"), "eggs"))
    st.add_setting(Setting(("foo", "bar", "number"), 123))
    st.add_setting(Setting(("foo", "bar", "thing"), "value"))
    st.show_map()
    st.show_tree()
    print()


### Tree


@dataclass
class Setting:
    path: TreePath
    raw_value: str
    real_value: Any | None = None
    is_leaf: bool = True


@dataclass
class Node:
    element: Setting
    parent: Node
    children: list[Node] = field(default_factory=list)

    @property
    def path(self):
        return self.element.path

    def __str__(self):
        return "Node(parent={}, child_count={}, setting={})".format(
            repr(self.parent.element.path[-1]),
            len(self.children),
            repr(self.element),
        )


class SettingNotFound(Exception):
    pass


class EmptyTreePath(Exception):
    pass


class EMTPY:
    pass


TreeMap = dict[TreePath, Node]


class SettingTree:
    def __init__(self, env: str = "default"):
        self.root = Node(Setting(("root",), ""), None)  # type: ignore
        self.root.parent = self.root
        self.tree_map: TreeMap = {self.root.path: self.root}
        self.env = env

    def add_dict(self, data: dict):
        ...

    def add_setting(self, setting: Setting) -> Node:
        """
        Add @setting and creates intermediary settings if necessary
        """
        path = setting.path
        new_node = self._add_setting(setting)

        # create non-leaf setting, if does not exit yet
        for i in range(1, len(path)):
            if not self.setting_exist(path[:i]):
                self._add_setting(Setting(path[:i], "", is_leaf=False))
        return new_node

    def _add_setting(self, setting: Setting) -> Node:
        """
        Add a single setting
        """
        path = setting.path
        try:
            parent = self._get_node(path[:-1])
        except SettingNotFound:
            parent = self._add_setting(Setting(path[:-1], "", is_leaf=False))
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
