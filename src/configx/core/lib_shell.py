"""
Module responsible for providing the final user interface for acessing data.
Should support most of legacy Dynaconf (v3) setting-acess behaviour.

Example:
    >>> data = {
            "name": "john",
            "info": {"age": 33, "married": True},
            "items": ["a", "b", {"c": "hello world"}]
        }
    >>> setting = SettingShell(SettingTree(data))

    >>> setting.name # too hard to implement
    "john"
    >>> setting["name"]
    "john"
    >>> setting.get("name")
    "john"
    >>> setting("name")
    "john"

    >>> setting.info.age
    33
    >>> setting.items[2].c
    "hello world"

Notes:
    - accessing the obj-dot-syntax path as Sequence[names] is too hard.
    >>> foo.bar.spam() # using call
    - later (implement the easier ones first), try pre-building a object,
      so it naturally supports dot-syntax.
"""
from __future__ import annotations

from typing import Any

from configx.core.setting_tree import Node, SettingTree, TreePath


def main():
    setting = SettingShell()
    setting.get("foo.bar")


MISSING: Any = object()


class SettingShell:
    """
    # setting query
    [x] 'get',
    [x] 'exists',
    [x] 'exists_in_environ',
    [x] 'get_environ',

    'to_dict',
    'as_bool',
    'as_dict',
    'as_float',
    'as_int',
    'as_json',

    'fresh',
    'get_fresh',
    'from_env',

    'is_overridden',
    'path_for',
    'find_file',

    # setting-modifiers
    'populate_obj',
    'set',
    'setdefault',
    'setenv',
    'update',
    'unset',
    'unset_all',
    'pre_load',
    'reload',

    'execute_loaders',
    'load_extra_yaml',
    'load_file',
    'load_includes',

    'clean',
    'configure',

    """

    def get(
        self,
        key: str,
        default: bool = MISSING,
        cast: bool = MISSING,
        fresh: bool = MISSING,
        dotted_lookup: bool = MISSING,
        sysenv_fallback: bool = MISSING,
    ) -> Any:
        """
        Get a value from settings store.
        This is the preferred way to access settings.

        @todo: add clarification

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :param fresh: Should reload from loaders store before access?
        :param dotted_lookup: Should perform dotted-path lookup?
        :param sysenv_fallback: Should fallback to system environ if not found?
        :return: The value if found, default or None

        Example:
            >>> from dynaconf import Dynaconf
            >>> settings = Dynaconf()
            >>> settings.update({"key": "hello world"})
            >>> settings.get('KEY')
            "hello world"

        Deprecated params:
            parent (since v4): used only for internal purposes
        """
        ...

    def get_fresh(
        self, key: str, default: Any = MISSING, cast: Any["@todo"] = MISSING
    ) -> Any:
        """
        This is a shortcut to `get(key, fresh=True)`.
        Always reload from loaders store before getting the var.

        @todo understand this behaviour better.

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
        :return: The value if found, default or None
        """
        ...

    def get_environ(
        self, key: str, default: Any = MISSING, cast: Any["@todo"] = MISSING
    ) -> Any:
        """
        Gets value from environment variable (uses `os.environ.get`).
        Optionally, sets default value and automatic casting of the value.

        :param key: The name of the setting value, will always be upper case
        :param default: In case of not found it will be returned
        :param cast: Should cast in to @int, @float, @bool or @json ?
         or cast must be true to use cast inference
        :return: The value if found, default or None
        """
        ...

    def exists(self, key: str, fresh: bool = MISSING) -> bool:
        """
        Return True if key exists in the active environment.

        :param key: the name of the setting variable
        :param fresh: if key should be taken from source directly
        :return: bool
        """
        ...

    def exists_in_environ(self, key: str):
        """
        Return True if key is exported in environment variable.
        @clarify: is there a way to write settings data to sysenv?
        """
        ...


def dot_notation_string_to_tree_path(dot_notation: str) -> TreePath:
    return tuple()


if __name__ == "__main__":
    exit(main())
