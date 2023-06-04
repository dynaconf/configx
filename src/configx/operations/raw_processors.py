"""
Operators that process (raw_string: str, context: ContextObject)

ContextObject is a generated from a SettingTree to allow for
dot notation lookup (for subsitutions, such as format)
"""

from typing import Any, Sequence

from configx.core.setting_tree import SettingTree
from configx.types import MISSING, ContextObject, TreePath


def build_context_from_tree(
    setting_tree: SettingTree, filter_by_paths: Sequence[TreePath] = MISSING
) -> ContextObject:
    ...


def build_context_from_dict(
    dict_data: dict, filter_by_paths: Sequence[TreePath] = MISSING
) -> ContextObject:
    ...


def bypass_processor(raw_string: str, context: ContextObject = MISSING) -> Any:
    return raw_string
