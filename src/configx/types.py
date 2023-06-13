"""
Shared Types for the project.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, NamedTuple, Protocol, Sequence, TypeAlias

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


TreePath = tuple[str | int, ...]  # ("path", "to", "setting")
TreeMap = dict[TreePath, "Node"]


SimpleTypes = int | str | float
CompoundTypes = list | dict
PrimitiveTypes = SimpleTypes | CompoundTypes

# Setting related


SettingSource = str  # unix-like file object aka identifier
SettingSourceType = Any  # unix-like file type aka loader


class RawValue(str):
    """Raw String with unparsed tokens"""


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

    def __call__(self, raw_string: str, context: ContextObject = MISSING) -> None:
        ...


TreePathGraph: TypeAlias = dict[TreePath, set[TreePath]]


class DependencyEdge(NamedTuple):
    dependent: TreePath
    depends_on: TreePath
