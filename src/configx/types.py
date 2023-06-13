"""
Shared Types for the project
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, NamedTuple, Protocol, Sequence, TypeAlias

if TYPE_CHECKING:
    pass


# Sentinel for non-provided arguments
MISSING: Any = object()

ContextObject: TypeAlias = SimpleNamespace


class RawProcessor(Protocol):
    """
    A raw string processing function.
    It should take a raw string (presumably without tokens) and a ContextObject
    (arbitrary object with attribute access) and return a processed value.
    """

    def __call__(self, raw_string: str, context: ContextObject = MISSING) -> None:
        ...


class RawData(NamedTuple):
    operators: Sequence[RawProcessor]
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
