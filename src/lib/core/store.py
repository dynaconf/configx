"""
Settings store abstraction class and helper components
"""
from __future__ import annotations

from lib.core.tree import Tree
from lib.shared.types import AllTypes, Environment, TreePath


class Store:
    """
    Store for settings.

    Responsible for controlling the core data structure (Tree)
    and provide user-level api on the stored settings.
    """


def create_settings_tree() -> Tree:
    """
    if Tree became a module this is deprecated
    """
    return Tree()


def create_settings(data: dict):
    """
    Validate, creates and store settings from python a dict.
    Doest't handle merging.
    Equivalent to dynaconf.update.
    """


def update_settings(data: dict):
    """
    Validate, creates and store @data as settings from python a dict.
    Handle merging.
    Equivalent to dynaconf.update.
    """


def delete_settings(path: TreePath):
    """
    Deletes settings from @path
    Equivalent to dynaconf.update.
    """
