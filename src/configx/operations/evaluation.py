"""
Evalution module.
Responsible for manipulating Setting inside SettingNodes

Example:
    >>> import evaluate
    >>> import SettingTree as ST

    >>> data = {
            "cast": "@int 123",
            "sub": "@format **{this.a}-{this.foo.b}**",
            "a": "hello",
            "foo": {"b": "world"}
        }
    >>> st = ST(data)
    >>> evalution.evaluate_tree(
            setting_tree=st,
            dynaconfig_tree=ST(),
        )

    >>> st.show_tree()
    "root": <dict>
        "cast": 123
        "sub": "**hello-world**"
        "a": "hello"
        "foo": <dict>
            "b": "world"
"""
from __future__ import annotations

from typing import Sequence

from configx.core.setting_tree import Node, SettingTree, TreePath


def evaluate(setting_tree: SettingTree, dynaconfig_tree: SettingTree):
    ...


def pre_evaluate_tree():
    ...


def pre_evaluate_node(node: Node) -> DependencyGraph:
    """
    Pre-evaluates nodes:
    - normalize lazy_string
        before: setting.raw_value = "@int 123"
        after:  setting.raw_value(int_parser, "123")

        before: setting.raw_value = "@format {this.name}"
        after:  setting.raw_value = "@format {this['name']}" (easier to use)

    - apply parser function (with no dependencies):
        before:
            setting.raw_value = (int_parser, "123")
            setting.real_value = None
        after:
            setting.raw_value = (int_parser, "123")
            setting.real_value = 123 <type int>

    - analyze substitution dependencies:
        with:
            setting.raw_value = (format_parser, "hello {this.name}")
        if:
            if ("name",) is not evaluated yet (not in setting.real_value)
        do:
            edge = (setting.path, ("name",)) # directed edge
            return DependecyGraph().add(edge)
    """
    ...


class NOT_EVALUATED:
    pass


class DependencyGraph:
    """
    Dependecy Graph.
    Responsible ordering/validating dependencies and returning
    nodes in proper order.
    """

    def add(self, node: Node, dependents: Sequence[TreePath]):
        """Add node dependency"""

    def dequeue(self) -> Node:
        """Return the next node"""
        ...

    def __len__(self):
        return 0
