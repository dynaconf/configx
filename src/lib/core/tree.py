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


class BaseNode:
    """
    Common behaviour for PathNode and LeafNode

    Also serves as root.
    """

    def __init__(
        self,
        parent: BaseNode | None = None,
        name: str = "",
        children: Children | None = None,
    ):
        self.parent = parent
        self.children = Bucket(children, owner=self) if children else None
        self.depth = 0
        self.__name = name
        self.__path = None

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    def is_root(self):
        return self.parent is None

    def show_path(self):
        print(self.get_full_path())

    def get_full_path(self):
        if not self.__path:
            self.__path = self.__get_full_path()
        return self.__path

    def __get_full_path(self):
        """
        Recursively get ancestor paths
        """
        path = self.parent.__get_full_path() if self.parent else ()
        return TreePath((*path, self.name))

    def __repr__(self):
        return f"""{self.__class__.__name__}(name='{self.name}')"""


class PathNode(BaseNode):
    """
    Responsible for holding shared path information for LeafNodes

    rules:
    - Cannot have `children=None` or `len(children) == 0`
    - Logical identify is based on immutable (full_path)
    """

    def __init__(
        self, name: str, parent: BaseNode | None, children: Children | None = None
    ):
        super().__init__(parent, name, children)
        # assures PathNode have a bucket
        if not self.children:
            self.children = Bucket()

    def inspect(self, mode="string_id"):
        """
        Inspecting object
        """
        return f"{self.get_identifier()} (children-length = {len(self.children)})"

    def get_identifier(self):
        return ".".join(self.get_full_path())

    def __hash__(self):
        return hash(self.get_full_path())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.get_full_path() == other.get_full_path()


class LeafNode(BaseNode):
    """
    Responsible for holding the Setting object

    rules:
    - Cannot have `children`
    - If `self.parent` is `A`, 'A.children' must contain `self`
    - Logical identify is based on immutable (full_path, env, source)

    notes:
    - for bucket indexing, hash wouldn't require (full_path, ...),
      only (name, ...). but there is no clear gain in making that distinction.
    """

    def __init__(self, setting: Setting, parent: BaseNode):
        super().__init__(parent, setting.name)
        self.setting = setting
        self.__id_tuple = (  # nobreak
            self.get_full_path(),
            self.setting.env,
            self.setting.source,
        )

    def __repr__(self):
        repr_template = """{}(name={}, raw_data={}, env={}, source={})"""
        return repr_template.format(
            self.__class__.__name__,
            repr(self.setting.name),
            repr(self.setting.raw_data),
            repr(self.setting.env),
            repr(self.setting.source),
        )

    def inspect(self, mode="string_id"):
        """
        Inspecting object
        """
        return f"{self.get_identifier()} = {repr(self.setting.raw_data)}"

    @property
    def identifier(self):
        """
        Immutable identifier tuple
        """
        return self.__id_tuple

    def get_identifier(self):
        """
        Pritable identifier
        """
        str_identifier = (".".join(self.identifier[0]), *self.identifier[1:])
        return "::".join(str(n) for n in str_identifier)

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.identifier == other.identifier


class Node:
    """
    - Inner nodes: Responsible for holding shared path/key information
    about a Settings
    - Leaves: Responsible for holding a Setting object

    TODO: consider creating different classes for them
    """

    def __init__(
        self,
        name: str,
        element: Setting | None = None,
        children: Children | None = None,
        parent: Node | None = None,
    ):
        self.name = name
        self.parent: Node | None = parent
        self.element = element
        self.children = Bucket(children) if children else []
        self.depth = 0

    def is_leaf(self):
        return not self.children and self.element

    def is_root(self):
        return self.parent is None

    def full_path(self):
        path = self.parent.full_path() if self.parent else ()
        return TreePath((*path, self.name))

    def relative_id_str(self):
        """
        Return relative id for node:
        - PathNode: ".name"
        - LeafNode: ".name::env::/abs/path/to/source"
        """
        if not self.is_leaf():
            return f".{self.name}"
        assert self.element
        rel_id_format = ".{}::{}::{}"
        return rel_id_format.format(self.name, self.element.env, self.element.source)

    def aboslute_id_str(self):
        """
        Return relative id for node:
        - PathNode: "full.path.to.name"
        - LeafNode: "full.path.to.name::env::/abs/path/to/source"
        """
        full_dotted_path = ".".join(self.full_path())
        if not self.is_leaf():
            return full_dotted_path
        assert self.element
        rel_id_format = "{}::{}::{}"
        return rel_id_format.format(
            full_dotted_path, self.element.env, self.element.source
        )

    def __repr__(self):
        parent_name = self.parent.name if self.parent else ""
        node_type = "LeafNode" if self.is_leaf() else "PathNode"
        return (
            f"""{node_type}(name="{self.name}", parent="{parent_name}","""
            f""" element={self.element}, children_len={len(self.children)})"""
        )

    def __getitem__(self, key):
        """
        Implement node['name'] access to children
        """

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
    path: TreePath | None = None

    @property
    def type(self):
        """
        Should be calculated from evaluated value
        """
        return "foo"


class Bucket:
    """
    The container for Nodes and Leaves

    Responsible for holding and efficiently acessing
    Node and Leaf objects.
    """

    def __init__(
        self, initial_nodes: Children | None = None, owner: BaseNode | None = None
    ):
        # initializes with optional initial list of nodes
        initial_data = []
        if initial_nodes:
            initial_data = [(n, n) for n in initial_nodes]
        self.__container = PositionalDict(initial_data)

        # Optionally provide the owner Node, for convenience
        self.owner = owner

    # Crud

    def append(self, item: BaseNode):
        """
        Append item to the last position
        """
        self.__container[item] = item

    def get_by_props(
        self,
        name: str,
        env: Environment | None = None,
        source: DataSource | None = None,
    ) -> list[Node]:
        """
        Get node by properties

        TODO implement env and data_source filters
        """
        return [n for n in self if n.name == name]

    def get_by_index(self, index: int) -> Node:
        """
        Get item by name
        """
        return self.__container[index]

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

    def inspect(self, verbose=0, relative_path=True):
        """
        Debugging function
        TODO see lib to pretty print these stuff
        """
        print("=" * 10)
        print(f"parent: {self.owner}")
        print(f"path: {self.owner.aboslute_id_str() if self.owner else None}")
        print(f"length: {self.__len__()}")
        print("=" * 10)
        sep = " " * 1

        for i, n in enumerate(self):
            if n.is_leaf():
                # extra_info = f" {sep}(raw_data='{n.element.raw_data}')"
                extra_info = f"{sep}('{n.element.raw_data}')"
            else:
                # extra_info = f" {sep}(children_len={len(n.children)})"
                extra_info = f"{sep}({len(n.children)})"
            show = extra_info if verbose else ""
            path = n.relative_id_str() if relative_path else n.aboslute_id_str()
            print(f"[{i}] {path}{show}")

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

    def __getitem__(self, key):
        return self.__container.__getitem__(key)


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

    Notes
    - Maybe Tree could be a module (singleton). This would avoid
    instance duplication and would provide better LRU caching
    """

    def __init__(self, root: BaseNode | None = None):
        self.root = BaseNode(None, "root")
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

    def get_nodes_by_path(self, path: TreePath) -> list[Node]:
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
