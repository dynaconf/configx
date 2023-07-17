from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

from configx.types import TreePath

if TYPE_CHECKING:
    from configx.core.setting_tree import Node


def tree_to_dict(node: Node) -> dict:
    """
    Converts a SettingTree to python structure (list and dicts).
    Args:
        node: the root node of the subtree to be converted
    Raises:
        NotEvaluatedError: tree has nodes without evaluation
    """
    ...


def str_to_tree_path(string: str):
    """
    Converts dot notation string to TreePath object.
    """
    tree_path: list[int | str] = []
    for s in string.split("."):
        try:
            tree_path.append(int(s))
        except ValueError:
            tree_path.append(s)

    return TreePath(tree_path)


def tree_path_to_str(tree_path: TreePath):
    """
    Converts a TreePath object to dot notation string.
    """
    return ".".join([str(v) for v in tree_path])


def assure_tree_path(path_or_node: TreePath | Node) -> TreePath:
    """
    Gets rooted TreePath from node or bypasses if already TreePath.
    """
    if isinstance(path_or_node, tuple):
        return path_or_node
    else:
        return path_or_node.rooted_path
