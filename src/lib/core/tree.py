"""
Holds the core data structure to hold and provide
essential operations over Setting objects consistently.
"""

from __future__ import annotations

from typing import Iterable

from lib.core.nodes import LeafNode, PathNode, Setting
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


class PathNotFoundError(Exception):
    pass


class MultipleNodesFoundError(Exception):
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
        self.root = PathNode("root", None, node_type=dict) # TODO fix this
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
            node_type, elements = normalize_compound_type(element)
            new_node = PathNode(name, parent, node_type=node_type)  # type: ignore
            parent.children.append(new_node)
            self.size += 1
            for k, v in elements.items():
                self.create_node(k, v, parent=new_node)
            return new_node

        raise TypeError("Param @element should be of type Setting or None")

    def replace_node(self, old_node: NodeType, new_node: NodeType) -> NodeType:
        """
        Replace node at @path by @new_node and return @old_node
        """
        parent = old_node.parent
        self.remove_node(old_node)
        new_node.parent = parent
        parent.children.append(new_node)  # every parent should be PathNode
        return old_node

    def remove_node(self, node: NodeType) -> NodeType:
        """
        Remove @node from tree and return removed Node
        """
        if not node.parent:
            raise TypeError("Node is a root, can't be removed")

        parent = node.parent  # every parent should be PathNode
        parent.children.remove_by_node_id(node.identifier)
        self.size -= 1
        return node

    def get_node_by_path(self, path: TreePath, default=None, first=False) -> NodeType:
        """
        Convenience function to return single node when
        there is just a single result.
        """
        try:
            nodes = self.get_nodes_by_path(path)
            if len(nodes) > 1 and first == False:
                raise MultipleNodesFoundError(
                    f"More than one node was found: {len(nodes)} nodes"
                )
            return nodes[0]
        except PathNotFoundError:
            if not default:
                raise
            return default

    def get_nodes_by_path(self, path: TreePath, default=None) -> list[NodeType]:
        """
        Get nodes by it's @path.
        More than one node can be located in the same @path
        because they can have different env and source value.

        Args:
            path: the path to the setting (without 'root')
        """
        try:
            result = get_nodes_by_path_from(self.root.children, path)
        except PathNotFoundError:
            if not default:
                raise
            return default

        return result if result else []

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


def get_nodes_by_path_from(
    nodes: Iterable[NodeType] | PathNode, path: TreePath, position: int = 0
) -> list[NodeType] | None:
    """
    Recursive function to find nodes at given path
    from a given iterable of nodes.

    NOTES:
        this may implement generators
        is this recursion efficient?

    Args:
        nodes: nodes that will be looked up
        path: the full path which the nodes must match
        position: the position of the path it will use here

    Raises:
        PathNotFoundError: when no node is found for given path
    """
    nodes = iter(nodes.children) if isinstance(nodes, PathNode) else nodes
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
    return get_nodes_by_path_from(path_node_children, path, position + 1)


def main():
    pass


if __name__ == "__main__":
    main()
