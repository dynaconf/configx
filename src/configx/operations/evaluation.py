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
from configx.types import DependencyEdge, LazyProcessor


def evaluate(setting_tree: SettingTree, dynaconfig_tree: SettingTree):
    ...


def pre_evaluate_tree(setting_tree: SettingTree) -> DependencyGraph:
    """
    Pre-evaluate all nodes of the tree and return DependencyGraph.
    """
    dependency_graph = DependencyGraph()
    for node in setting_tree:
        edges = pre_evaluate_node(node)
        for edge in edges:
            dependency_graph.add_edge(edge)
    return dependency_graph


def pre_evaluate_node(node: Node) -> Sequence[DependencyEdge]:
    """
    Pre-evaluates a single node:
    - normalize string with tokens.
        E.g: "@int 123" -> ((int_converter,), "123") type: LazyProcessor
    - apply parser function (with no dependencies):
        E.g: (int_converter, "123") -> s.real_value=123
    - return substitution dependencies:
        E.g: For node with path ("original", "setting")
        with raw_value: (format_parser, "hello {this.other.setting}")
        return:         DependencyEdge(("original", "setting"), ("other", "setting"))
    """
    # normalize string tokens
    lazy_processor = _normalize_string_tokens(str(node.element.raw_value))
    node.element.raw_value = lazy_processor
    real_value = NOT_EVALUATED  # is this needed?

    # apply parser funcions if no dependencies
    dependencies = []
    if SUBSTITUTION_OPERATORS in lazy_processor.operators:
        dependencies = _get_substitution_dependencies(lazy_processor.raw_value)
    if not dependencies:
        node.element.real_value = _apply_lazy_processor(lazy_processor)

    # return dependencie edges
    dependencie_edges = []
    if dependencies:
        dependencie_edges = [
            DependencyEdge(node.path, dependency) for dependency in dependencies
        ]
    return dependencie_edges


def _normalize_string_tokens(string_with_token: str) -> LazyProcessor:
    """Transforms string with tokens into LazyProcessor"""
    ...
    return LazyProcessor([lambda x: x], string_with_token)


def _get_substitution_dependencies(string: str) -> Sequence[TreePath]:
    """Get substitution dependencies, otherwise returns []"""
    ...


def _apply_lazy_processor(lazy_processor: LazyProcessor):
    """
    Apply lazy_processor operations and return processed value
    Assumes lazy_processor has no dependencies.
    """
    value = lazy_processor.raw_value
    for operator in lazy_processor.operators:
        value = operator(value)
    return value


SUBSTITUTION_OPERATORS = [lambda x: x, lambda x: x]


class NOT_EVALUATED:
    pass


class DependencyGraph:
    """
    Dependecy Graph.
    Responsible ordering/validating dependencies and returning
    nodes in proper order.
    """

    def add_edge(self, edge: DependencyEdge):
        """Add node dependency"""
        ...

    def clear(self) -> Node:
        """Clear graph vertex and edges"""
        ...

    def _validate(self):
        """Validate graph non-circularity"""
        ...

    def __iter__(self):
        """Return vertex (TreePath) iterator in proper_order"""

    def __len__(self):
        return 0
