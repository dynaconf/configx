"""
Shared exceptions for the project.
"""

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
    pass


class InvalidTokenError(Exception):
    pass


class TokenError(Exception):
    pass
