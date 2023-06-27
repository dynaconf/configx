"""
Evalution module.
Responsible for manipulating Setting values state (raw -> lazy -> real)
    - Trivial-evaluate: raw -> real (non-strings and not-startswith "@")
    - Pre-evaluate: raw -> lazy
    - Evaluate: lazy -> real

Example:
    >>> from configx.services.evaluation.api import evaluate_tree
    >>> from configx.core.setting_tree import SettingTree

    >>> data = {
            "cast": "@int 123",
            "sub": "@format **{this.a}-{this.foo.b}**",
            "a": "hello",
            "foo": {"b": "world"}
        }
    >>> st = SettingTree()
    >>> st.populate(data)
    >>> api.evaluate_tree(
            setting_tree=st
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

from graphlib import CycleError
from typing import TYPE_CHECKING, Sequence

from configx.exceptions import MissingContextValue
from configx.services.evaluation.dependency_graph import DependencyGraph
from configx.services.evaluation.processors_core import (
    SUBSTITUTION_OPERATORS,
    build_context_from_tree,
    get_processor,
)
from configx.services.evaluation.utils import (
    _apply_lazy_processors,
    _parse_raw_value_tokens,
)
from configx.types import DependencyEdge, LazyValue

if TYPE_CHECKING:
    from configx.core.setting_tree import Node, SettingTree


def main():
    """Usage samples"""
    ...


def evaluate_tree(setting_tree: SettingTree, internal_config_tree: SettingTree):
    """Evaluate a tree in-place"""
    dependency_graph = pre_evaluate_tree(setting_tree)
    evaluate_tree_dependencies(setting_tree, dependency_graph)


def evaluate_tree_dependencies(
    setting_tree: SettingTree, dependency_graph: DependencyGraph
) -> SettingTree:
    """
    Evaluate setting_tree dependencies only.

    May raise an error if Setting doesn't have LazyValue
    """
    try:
        topological_order = dependency_graph.items()
    except CycleError:
        raise

    for path, dependencies in topological_order:
        node = setting_tree.get_node(path)
        context = build_context_from_tree(setting_tree, dependencies)

        # should be pre-evaluated
        assert isinstance(node.element._raw_value, LazyValue)
        node.element.real_value = _apply_lazy_processors(
            lazy_value=node.element._raw_value, context=context
        )
    return setting_tree


def pre_evaluate_tree(setting_tree: SettingTree) -> DependencyGraph:
    """
    Pre-evaluate all nodes of the tree and return DependencyGraph.
    """
    dependency_graph = DependencyGraph()
    for node in setting_tree:
        edges = pre_evaluate_node(node)
        edges = [edge for edge in edges if edge.depends_on]
        dependency_graph.add_edges(edges)
    return dependency_graph


def pre_evaluate_node(node: Node) -> Sequence[DependencyEdge]:
    """
    Pre-evaluates a single node and return it's dependencies.

    - convert raw to lazy or bypass
        "@int 123" -> LazyValue(processors=[int_converter], raw_string="123")
        "123" -> LazyValue(processors=[], raw_string="123")

    - apply parser function (with no dependencies):
        E.g: (int_converter, "123") -> s.real_value=123

    - return substitution dependencies:
        E.g: For node with path ("original", "setting")
        with raw_value: (format_parser, "hello {this.other.setting}")
        return:         [DependencyEdge(("original", "setting"), ("other", "setting"))]

    TODO (after working example)
        - enforce non-string values are bypassed on Setting init or raw_value set.
          this should simplify raw-lazy-real state management
    """
    # trivial convert: raw -> real (non-string and not-startwith @)
    # this could be done in the SettingTree level
    if not isinstance(
        node.element._raw_value, str
    ) or not node.element._raw_value.startswith("@"):
        node.element.real_value = node.element.raw_value
        return []

    # convert: raw -> lazy
    token_names, raw_string = _parse_raw_value_tokens(node.element._raw_value)
    processor_list = [get_processor(token) for token in token_names]
    lazy_value = LazyValue(operators=processor_list, string=raw_string)
    node.element._raw_value = lazy_value

    # apply lazy processors or collect dependencies
    dependency_edges = []
    try:
        node.element.real_value = _apply_lazy_processors(lazy_value)
    except MissingContextValue as err:
        dependency_edges = [
            DependencyEdge(node.path, ("root", *dep[1:])) for dep in err.dependencies
        ]
        # could retry to evalute it here if a setting_tree or some kind of
        # global context is passed
    return dependency_edges
