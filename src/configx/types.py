"""
Shared Types for the project
"""
from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    pass


SimpleTypes = int | str | float
CompoundTypes = list | dict
PrimitiveTypes = SimpleTypes | CompoundTypes

Raw = str  # should be class
Environment = str  # should be class

SettingSource = str  # unix-like file object
TreePath = tuple[str | int, ...]  # ("path", "to", "setting")
