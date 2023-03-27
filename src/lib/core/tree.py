"""
Holds the core data structure to hold and provide
essential operations over Setting objects consistently.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, OrderedDict, Sequence

from lib.shared.types import *
from lib.shared.utils import normalize_compound_type


def main():
    """Quick testing"""


# main components


class Node:
    """
    - Inner nodes: Responsible for holding shared path/key information
    about a Settings
    - Leaves: Responsible for holding a Setting object
    """

    def __init__(
        self,
        name: str,
        element: Setting | None,
        children: Children | None = None,
        parent: Node | None = None,
    ):
        self.name = name
        self.parent: Node | None = parent
        self.element = element
        self.children = Bucket(children)
        self.depth = 0

    def is_leaf(self, node: Node):
        return node.children is None

    def is_root(self, node: Node):
        return node.parent is None

    def full_path(self):
        path = self.parent.full_path() if self.parent else ()
        return TreePath((*path, self.name))

    def __repr__(self):
        parent_name = self.parent.name if self.parent else ""
        return (
            f"""(name="{self.name}", parent="{parent_name}", element={self.element})"""
        )

    def __len__(self):
        return len(self.children)


@dataclass
class Setting:
    """
    Data Structure to Setting data
    """

    name: str
    raw_data: Raw | SimpleTypes
    source: DataSource = "programmatic"
    env: Environment = "default"
    evaluated: SimpleTypes | None = None

    @property
    def type(self):
        return "foo"


# class Setting:
#     """
#     Data Structure to Setting data
#     """

#     def __init__(self, name:str, raw_data: Raw | SimpleTypes):
#         self.name: str = name
#         self.raw_data: Raw = raw_data
#         self.source: DataSource = "programmatic"
#         self.env: Environment = "default"
#         self.evaluated: SimpleTypes | None = None
#         self.type: type[AllTypes]


class Bucket:
    """
    The container for Nodes and Leaves

    Responsible for holding and efficiently acessing
    Node and Leaf objects.
    """

    def __init__(self, initial_nodes: Children | None = None):
        # self.parent = parent
        self.__container = PositionalDict()

    # Crud

    def append(self, item: Node):
        """
        Append item at the end
        """
        self.__container[item] = item

    def get_by_name(self, name: str):
        """
        Get item by name
        """

    def get_by_index(self, index: int):
        """
        Get item by name
        """

    # Iterators

    def nodes(self):
        """
        Return Generator with all items (Node)
        """
        return self

    def leaves(self):
        """
        Return Generator with only leaf nodes
        """
        return (n for n in self if n.is_leaf())

    def inner_nodes(self):
        """
        Return Generator with only leaf nodes
        """
        return (n for n in self if not n.is_leaf())

    # Dunder

    def __len__(self):
        return len(self.__container)

    def __iter__(self):
        yield from self.__container

    def __str__(self):
        return "\n".join(str(n) for n in self)

    def __delitem__(self, key: int | Node):
        """
        del B[i]
        del B[BucketItem]
        """


class PositionalDict(OrderedDict):
    """
    Data Structure to hold Node and Leaf by key and index

    It will use a name for hash-based lookup or
    a positional index.

    Notes on Current implemenation

        - has index lookup in O(n). This can be improved by holding data
        in both list and dict, but should use more memory.

        - for handling key-duplicates, it will require a Key object
        that will account for uniquness.

        This will be fast for queries of a specific Setting/Env/Src,
        but it may need optimizations for retriving incomplete queries.

    """

    def __getitem__(self, key):
        """
        Support for indexable search
        """
        if isinstance(key, str):
            return super().__getitem__(key)
        else:
            if isinstance(key, slice):
                raise TypeError("slices are not supported yet")
            elif isinstance(key, int):
                # support for negative index
                if key < 0:
                    key = len(self) + key

                # range check
                if key >= len(self) or key < 0:
                    raise IndexError()

                # get node in O(n)
                for index, node in enumerate(self.values()):
                    if index == key:
                        return node
        raise TypeError(
            f"Key of type {type(key)} is not supported. Should be of type int or str"
        )


# tree


class Tree:
    """
    The core tree which holds Setting objects

    Resonsible for manipulating Setting objects consistently
    """

    def __init__(self, root: Node | None = None):
        self.root = Node(name="root", element=None, parent=root)
        self.size: int = 0

    # CRUD

    def create_node(
        self,
        name: str,
        element: AllTypes,
        parent: Node | None = None,
        env: Environment = "default",
        source: DataSource = "programmatic",
    ) -> Node:
        """
        Create @element as child of @parent and return created Node
        """
        if parent is None:
            parent = self.root

        if isinstance(element, SimpleTypes | Raw):
            new_setting = Setting(name, element)
            new_node = Node(name=name, parent=parent, element=new_setting)
            parent.children.append(new_node)
            return new_node
        if isinstance(element, CompoundTypes):
            new_node = Node(name=name, parent=parent, element=None)
            elements = normalize_compound_type(element)
            for k, v in elements.items():
                # breakpoint()
                self.create_node(k, v, parent=new_node)
            parent.children.append(new_node)
            return new_node

        raise TypeError("Param @element should be of type Setting or None")

    def get_node_by_path(self, path: TreePath) -> Node:
        """
        Get node by it's TreePath.
        Eg: ("path", "to", "setting")
        """
        ...

    def remove_node(self, node: Node) -> Node:
        """
        Remove @node from tree and return removed Node
        """
        ...

    # Utils

    def is_empty(self):
        return not self.size

    def height(self):
        pass

    def show(self):
        """Pre-order algorithm to show tree structure"""
        self._show(self.root)

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
