"""
Shared Types for the project
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NamedTuple, Sequence

if TYPE_CHECKING:
    pass


class LazyProcessor(NamedTuple):
    operators: Sequence[Callable]
    raw_value: str


class DependencyEdge(NamedTuple):
    dependent: TreePath
    depends_on: TreePath


SimpleTypes = int | str | float
CompoundTypes = list | dict
PrimitiveTypes = SimpleTypes | CompoundTypes

Raw = str  # should be class
Environment = str  # should be class

SettingSource = str  # unix-like file object
TreePath = tuple[str | int, ...]  # ("path", "to", "setting")
