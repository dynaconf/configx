from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from lib.core.bucket import Bucket
from lib.shared.types import *

PathNodeTypes = dict | list


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
        node_type: PathNodeTypes | None = None,
    ):
        self.parent = parent
        self.children = Bucket(children, owner=self) if children else None
        self.depth = 0
        self.__name = name
        self.__path = None
        self.__type = node_type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def value(self) -> str:
        """Trivial implementation for convenience of printing nodes as key,val"""
        return ""

    @property
    def type(self) -> PathNodeTypes | None:
        return self.__type

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

    def __hash__(self):
        return hash(self.get_full_path())

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
        self,
        name: str,
        parent: PathNode | None,
        children: Children | None = None,
        node_type: PathNodeTypes | None = None,
    ):
        super().__init__(parent, name, children, node_type=node_type)
        # assures PathNode have a bucket
        if not self.children:
            self.children = Bucket()

        self.__id = NodeId(self.get_full_path())

    def inspect(self, mode="string_id"):
        """
        Inspecting object
        """
        return f"{self.get_identifier()} (children-length = {len(self.children)})"

    def get_identifier(self):
        return ".".join(self.get_full_path())

    @property
    def identifier(self):
        return self.__id

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

    def __init__(self, setting: Setting, parent: PathNode | None):
        super().__init__(parent, setting.name)
        self.setting = setting
        self.__id = NodeId(self.get_full_path(), self.setting.env, self.setting.source)

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
    def value(self):
        """
        Conveniece for printing node value
        """
        return self.setting.raw_data

    @property
    def identifier(self):
        """
        Immutable identifier tuple
        """
        return self.__id

    def get_identifier(self):
        """
        Printable identifier
        """
        str_identifier = (
            ".".join(self.identifier.path),
            self.identifier.env,
            self.identifier.source,
        )
        return "::".join(str(n) for n in str_identifier)

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.identifier == other.identifier


class NodeId(NamedTuple):
    """
    Node identifier
    """

    path: TreePath
    env: Environment | None = None
    source: DataSource | None = None


@dataclass
class Setting:
    """
    Data Structure to Setting data
    """

    name: str
    raw_data: Raw | SimpleTypes
    env: Environment = "default"
    source: DataSource = "programmatic"
    evaluated: SimpleTypes | None = None
    path: TreePath | None = None

    @property
    def type(self):
        """
        Should be calculated from evaluated value
        """
        return "foo"
