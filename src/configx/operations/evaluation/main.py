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

from collections import defaultdict
from graphlib import CycleError, TopologicalSorter
from typing import Any, Generator, Sequence, TypeAlias

from configx.core.setting_tree import Node, SettingTree, TreePath
from configx.operations.evaluation.processors import build_context_from_tree, get_processor
from configx.public.lib_shell import MISSING
from configx.types import ContextObject, DependencyEdge, RawData, RawProcessor


def evaluate(setting_tree: SettingTree, internal_config_tree: SettingTree):
    ...


def evaluate_tree_dependencies(
    setting_tree: SettingTree, dependency_graph: DependencyGraph
) -> SettingTree:
    """
    Evaluate setting_tree dependencies only.
    Assumes setting_tree is pre-evaluated.
    """
    try:
        topological_order = dependency_graph.items()
    except CycleError:
        raise

    for path, dependencies in topological_order:
        node = setting_tree._get_node(path)
        context = build_context_from_tree(setting_tree, dependencies)

        # should be pre-evaluated
        assert isinstance(node.element.raw_value, RawData)
        node.element.real_value = _apply_lazy_processor(
            lazy_processor=node.element.raw_value, context=context
        )
    return setting_tree


def pre_evaluate_tree(setting_tree: SettingTree) -> DependencyGraph:
    """
    Pre-evaluate all nodes of the tree and return DependencyGraph.

    possible optimization:
        Could try to evaluate dependency directly, so if they are
        luckily pre-evaluated in the proper order there is no
        need for a second pass using dependency_graph
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
        return:         [DependencyEdge(("original", "setting"), ("other", "setting"))]
    """
    # normalize string tokens
    lazy_processor = _normalize_string_tokens(str(node.element.raw_value))
    node.element.raw_value = lazy_processor
    real_value = NOT_EVALUATED  # is this needed?

    # apply parser funcions if no dependencies
    dependencies = []
    if SUBSTITUTION_OPERATORS in lazy_processor.operators:
        dependencies = _get_substitution_dependencies(lazy_processor.raw_value)
        # should dependencies be kept inside Setting? Maybe it can be convenient
    if not dependencies:
        node.element.real_value = _apply_lazy_processor(lazy_processor)

    # return dependencie edges
    dependencie_edges = []
    if dependencies:
        dependencie_edges = [
            DependencyEdge(node.path, dependency) for dependency in dependencies
        ]
    return dependencie_edges


def _normalize_string_tokens(string_with_token: str) -> RawData:
    """Transforms string with tokens into LazyProcessor"""
    placeholder = get_processor("bypass")
    return RawData([placeholder], string_with_token)


def _get_substitution_dependencies(string: str) -> Sequence[TreePath]:
    """Get substitution dependencies, otherwise returns []"""
    ...


def _apply_lazy_processor(
    lazy_processor: RawData, context: ContextObject = MISSING
):
    """
    Apply lazy_processor operations and return processed value
    Assumes outer context won't allow context with missing dependencies.
    """
    context_object = context if not MISSING else ContextObject()
    value = lazy_processor.raw_value
    for operator in lazy_processor.operators:
        value = operator(value, context_object)
    return value


SUBSTITUTION_OPERATORS = [lambda x: x, lambda x: x]


class NOT_EVALUATED:
    pass


TreePathGraph: TypeAlias = dict[TreePath, set[TreePath]]


class DependencyGraph:
    """
    Dependecy Graph.
    Responsible ordering/validating dependencies and returning
    nodes in proper order.
    """

    def __init__(self):
        self._graph: TreePathGraph = defaultdict(set)

    def add_edge(self, edge: DependencyEdge):
        """Add node dependency"""
        self._graph[edge.dependent].add(edge.depends_on)

    def clear(self):
        """Clear graph vertex and edges"""
        self._graph: TreePathGraph = defaultdict(set)

    def items(self) -> Generator[tuple[TreePath, Sequence[TreePath]], Any, Any]:
        """
        Yields tuple of dependent and its dependency sequence in topological order.
        """
        topological_sorter = TopologicalSorter(self._graph)
        for dependent in topological_sorter.static_order():
            yield (dependent, [*self._graph[dependent]])

    def __iter__(self):
        """Same as items()"""
        return self.items()

    def __len__(self):
        return len(self._graph)
