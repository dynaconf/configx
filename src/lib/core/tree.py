"""
Holds the core data structure to hold and provide
essential operations over Setting objects consistently.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from lib.core.bucket import Bucket
from lib.core.nodes import BaseNode, LeafNode, PathNode, Setting
from lib.shared.types import (
    AllTypes,
    CompoundTypes,
    DataSource,
    Environment,
    NodeType,
    Raw,
    SimpleTypes,
    TreePath,
)
from lib.shared.utils import normalize_compound_type


def main():
    """Quick testing"""
    t = Tree()
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

    path = ("spam", "nested")
    a = t.get_nodes_by_path(path)
    [print(n) for n in a]

    # print tree
    t.show()


class PathNotFoundError(Exception):
    pass


class Tree:
    """
    The core tree which holds Setting objects

    Resonsible for manipulating Setting objects consistently

    Notes
    - Maybe Tree could be a module (singleton). This would avoid
    instance duplication and would provide better LRU caching
    """

    def __init__(self):
        self.root = PathNode("root", None)
        self.size: int = 0

    # CRUD

    def create_node(
        self,
        name: str,
        element: AllTypes,
        parent: PathNode | None = None,
        env: Environment = "default",
        source: DataSource = "programmatic",
    ) -> NodeType:
        """
        Create @element as child of @parent and return created Node.
        If @element is a compound type, recursively creates other nodes.
        """
        if parent is None:
            parent = self.root

        if isinstance(element, SimpleTypes | Raw):
            new_setting = Setting(name, element, env=env, source=source)
            new_node = LeafNode(new_setting, parent)
            parent.children.append(new_node)
            self.size += 1
            return new_node

        if isinstance(element, CompoundTypes):
            new_node = PathNode(name, parent)
            elements = normalize_compound_type(element)
            parent.children.append(new_node)
            self.size += 1
            for k, v in elements.items():
                self.create_node(k, v, parent=new_node)
            return new_node

        raise TypeError("Param @element should be of type Setting or None")

    def get_nodes_by_path(self, path: TreePath) -> Iterable[NodeType]:
        """
        Get nodes by it's @path.
        More than one node can be located in the same @path
        because they can have different env and source value.

        Eg:
        ```
        t.get_nodes_by_path(("path", "to", "setting"))
        -> [Node('setting', env='default'), Node('setting'), env='production']
        ```
        """
        try:
            result = self._get_nodes_by_path(self.root.children, path)
        except PathNotFoundError:
            return []

        return result if result else []

    def _get_nodes_by_path(
        self, nodes: Iterable[NodeType], path: TreePath, position: int = 0
    ) -> Iterable[NodeType] | None:
        """
        Recursive function to find nodes with given path
        """
        match_nodes = [n for n in nodes if n.name == path[position]]

        # base case: not found
        if not len(match_nodes):
            raise PathNotFoundError(f"Path does not exist: {repr(path)}")

        # base case: last path position, return results
        if position == len(path) - 1:
            return match_nodes

        # not final path yet
        path_node = [n.children for n in match_nodes if isinstance(n, PathNode)]
        path_node_children = path_node[0] if path_node else []
        return self._get_nodes_by_path(path_node_children, path, position + 1)

    def remove_node(self, node: NodeType) -> NodeType:
        """
        Remove @node from tree and return removed Node
        """
        ...

    # Utils

    def is_empty(self):
        return not self.size

    def height(self):
        pass

    def show(self, root=None, verbose=0, style=None):
        """
        Show tree structure from @root
        """
        print(f"size={len(self)}")
        if style == "flat":
            self._show_flat(self.root)
            return
        root = root or self.root
        self._show(root, verbose=verbose)

    def _show(self, node: NodeType, indent=0, verbose=0):
        spacing = "   "

        node_value = repr(node.value) if node.value else ""
        node_repr = f"{node.name}: {node_value}"

        if verbose == 1:
            node_repr = repr(node)

        print(f"{indent * spacing}{node_repr}")

        if isinstance(node, PathNode):
            for n in node.children:
                self._show(n, indent + 1, verbose)

    def _show_flat(self, node: NodeType):
        spacing = "    "
        node_repr = f"{node.__class__.__name__}{spacing}{node.get_identifier()}"
        print(node_repr)

        if isinstance(node, PathNode):
            for n in node.children:
                self._show_flat(n)

    # Generators

    def iter_preorder(self):
        """
        Pre-order generator
        """

    def iter_postorder(self):
        """
        Post-order generator
        """

    def iter_levelorder(self):
        """
        Level-order (breadth-first) generator
        """

    # Dunder

    def __len__(self):
        return self.size


# Types


if __name__ == "__main__":
    main()
