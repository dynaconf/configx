"""
Holds the core data structure to hold and provide
essential operations over Setting objects consistently.
"""
from __future__ import annotations

from dataclasses import dataclass

from lib.core.bucket import Bucket
from lib.core.nodes import BaseNode, LeafNode, PathNode, Setting
from lib.shared.types import *
from lib.shared.utils import normalize_compound_type


def main():
    """Quick testing"""


# main components


# tree


class Tree:
    """
    The core tree which holds Setting objects

    Resonsible for manipulating Setting objects consistently

    Notes
    - Maybe Tree could be a module (singleton). This would avoid
    instance duplication and would provide better LRU caching
    """

    def __init__(self, root: BaseNode | None = None):
        self.root = PathNode("root", None)
        self.size: int = 0

    # CRUD

    def create_node(
        self,
        name: str,
        element: AllTypes,
        parent: NodeType | None = None,
        env: Environment = "default",
        source: DataSource = "programmatic",
    ) -> NodeType:
        """
        Create @element as child of @parent and return created Node
        """
        if parent is None:
            parent = self.root

        if isinstance(element, SimpleTypes | Raw):
            new_setting = Setting(name, element)
            new_node = LeafNode(new_setting, parent)
            parent.children.append(new_node)
            return new_node

        if isinstance(element, CompoundTypes):
            new_node = PathNode(name,parent)
            elements = normalize_compound_type(element)
            for k, v in elements.items():
                # breakpoint()
                self.create_node(k, v, parent=new_node)
            parent.children.append(new_node)
            return new_node

        raise TypeError("Param @element should be of type Setting or None")

    def get_nodes_by_path(self, path: TreePath) -> list[NodeType]:
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
        for p in path:
            self.root.children[p]
        ...

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

    def show(self, root=None):
        """
        Show tree structure from @root
        """
        root = root or self.root
        self._show(root)

    def _show(self, node, indent=0):
        spacing = "    "
        if node.element:
            raw = node.element.raw_data
            node_type = type(raw).__name__
            print(f"{indent * spacing}{node.name} ({node_type}): {raw}")
        else:
            node_len = len(node.children)
            node_type = "compound"
            print(f"{indent * spacing}{node.name} ({node_type}): len={node_len}")

        for n in node.children:
            self._show(n, indent + 1)

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
