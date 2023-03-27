"""
Shared Types for the project
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

# cicular import workaround
if TYPE_CHECKING:
    from lib.core.tree import Node
else:
    Node = object

# TODO resolve possible circular import issues

SimpleTypes = int | str | float
CompoundTypes = list | dict
AllTypes = SimpleTypes | CompoundTypes

Raw = str  # should be class
Environment = str  # should be class
DataSource = str  # should be class

Children = None | Sequence[Node]
TreePath = tuple[str]  # ("path", "to", "setting")
