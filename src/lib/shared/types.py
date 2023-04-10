"""
Shared Types for the project
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, TypeAlias

# cicular import workaround
if TYPE_CHECKING:
    from lib.core.nodes import BaseNode, LeafNode, PathNode
else:
    # hack
    BaseNode = object
    LeafNode = object
    PathNode = object

# TODO make this the source of types, to try to avoid circular imports
# BaseNode: TypeAlias = BaseNode
# LeafNode: TypeAlias = LeafNode
# PathNode: TypeAlias = PathNode

# TODO resolve possible circular import issues

SimpleTypes = int | str | float
CompoundTypes = list | dict
AllTypes = SimpleTypes | CompoundTypes

Raw = str  # should be class
Environment = str  # should be class
DataSource = str  # should be class

Children = None | Sequence[BaseNode]
TreePath = tuple[str, ...]  # ("path", "to", "setting")

NodeType: TypeAlias = LeafNode | PathNode
