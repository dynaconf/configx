"""
Shared Types for the project.
"""
from __future__ import annotations

import builtins
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    Any,
    NamedTuple,
    NewType,
    Protocol,
    Sequence,
    TypeAlias,
)

if TYPE_CHECKING:
    from configx.core.setting_tree import Node


# Sentinels
# related: https://peps.python.org/pep-0661/


class MissingType(Any):
    def __repr__(self):
        return "<MISSING>"


class NotEvaluatedType:
    def __repr__(self):
        return "<NOT_EVALUATED>"


MISSING = MissingType()
NOT_EVALUATED = NotEvaluatedType()


# SettingTree


TreePath = tuple[str | int, ...]


# class TreePath(tuple):
#     """
#     Representation of a TreePath.
#     TODO: enforce typing as tuple[str|int]
#     """

#     # def __getitem__(self, index_or_slice: int | slice):
#     #     match index_or_slice:
#     #         case builtins.slice:
#     #             return TreePath(super().__getitem__(index_or_slice))
#     #         case builtins.int:
#     #             return super().__getitem__(index_or_slice)

#     @classmethod
#     def from_str(cls, path: str) -> TreePath:
#         """
#         Construct TreePath from string.
#         Prefer using regular tuple constructor.

#         Examples:
#             >>> TreePath.from_str("foo.bar.spam")
#             TreePath("foo", "bar", "spam")

#         """
#         path_list = []
#         for key in path.split("."):
#             try:
#                 path_list.append(int(key))
#             except ValueError:
#                 path_list.append(key)
#         return cls(path_list)

#     def __str__(self):
#         """Should be used for displaying only"""
#         return ".".join(str(x) for x in self)


TreeMap = dict[TreePath, "Node"]


SimpleTypes = int | str | float
CompoundTypes = list | dict
PrimitiveTypes = SimpleTypes | CompoundTypes

# Setting related


SettingSource = str  # unix-like file object aka identifier
SettingSourceType = Any  # unix-like file type aka loader


class RawValue(str):
    """Ra" String with unparsed tokens"""


class LazyValue(NamedTuple):
    """Structure ready to be evaluated. Holds processors (parsed tokens) and raw strings."""

    operators: Sequence[RawProcessor]
    string: str


class RealValue(Any):
    """Evaluated value"""


# Evaluation


class ContextObject(SimpleNamespace):
    """
    Arbritrary object to allow for object-dot access (e.g, for format)
    """


class RawProcessor(Protocol):
    """
    A function that transforms a raw string into a new value,
    optionaly using a context object.
    """

    def __call__(self, raw_string: str, context: dict = MISSING) -> None:
        ...


TreePathGraph: TypeAlias = dict[TreePath, set[TreePath]]


class DependencyEdge(NamedTuple):
    dependent: TreePath
    depends_on: TreePath
