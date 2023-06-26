"""
Shared exceptions for the project.
"""

from typing import Sequence

from configx.types import TreePath

# SettingTree


class SettingNotFound(Exception):
    pass


class NodeNotFound(Exception):
    pass


class EmptyTreePath(Exception):
    pass


class ChildAlreadyExist(Exception):
    pass


# Evaluation


class LazyValueFound(Exception):
    pass


class MissingContextValue(Exception):
    """Raises when context does not have required dependency"""

    def __init__(self, dependencies: Sequence[TreePath], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dependencies = dependencies


class InvalidTokenError(Exception):
    pass


class TokenError(Exception):
    pass
