"""
Evalution module.
Responsible for manipulating Setting values inside Nodes

Example:
    >>> import evaluate
    >>> import SettingTree

    >>> data = {
            "cast": "@int 123",
            "sub": "@format **{this.a}-{this.foo.b}**",
            "a": "hello",
            "foo": {"b": "world"}
        }
    >>> st = SettingTree(data)
    >>> evalution.evaluate_tree(
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

from collections import defaultdict
from graphlib import CycleError, TopologicalSorter
from typing import TYPE_CHECKING, Any, Generator, Sequence, TypeAlias

from configx.actions.evaluation.processors import (
    SUBSTITUTION_OPERATORS,
    build_context_from_tree,
    get_processor,
)
from configx.types import (
    MISSING,
    ContextObject,
    DependencyEdge,
    LazyValue,
    TreePath,
    TreePathGraph,
)

if TYPE_CHECKING:
    from configx.core.setting_tree import Node, SettingTree


def main():
    """Usage samples"""
    ...


def evaluate_tree(setting_tree: SettingTree, internal_config_tree: SettingTree):
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
        node = setting_tree.get_node(path)
        context = build_context_from_tree(setting_tree, dependencies)

        # should be pre-evaluated
        assert isinstance(node.element.raw_value, LazyValue)
        node.element.real_value = _apply_lazy_processors(
            lazy_value=node.element.raw_value, context=context
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
        dependency_graph.add_edges(edges)
    return dependency_graph


def pre_evaluate_node(node: Node) -> Sequence[DependencyEdge]:
    """
    Pre-evaluates a single node:

    - normalize string with tokens to RawData type:
        E.g: "@int 123" -> LazyValue(processors=[int_converter], raw_string="123")

    - apply parser function (with no dependencies):
        E.g: (int_converter, "123") -> s.real_value=123

    - return substitution dependencies:
        E.g: For node with path ("original", "setting")
        with raw_value: (format_parser, "hello {this.other.setting}")
        return:         [DependencyEdge(("original", "setting"), ("other", "setting"))]
    """
    if node.is_pre_evaluated:
        return []

    # normalize string tokens
    lazy_value = _parse_raw_to_lazy_value(str(node.element.raw_value))
    node.element.raw_value = lazy_value

    # apply parser functions if no dependencies
    dependencies = []
    if SUBSTITUTION_OPERATORS in lazy_value.operators:
        dependencies = _get_substitution_dependencies(lazy_value.string)

    dependencie_edges = []
    if not dependencies:
        node.element.real_value = _apply_lazy_processors(lazy_value)

    # return dependencie edges
    else:
        dependencie_edges = [
            DependencyEdge(node.path, dependency) for dependency in dependencies
        ]
    return dependencie_edges


def _parse_raw_to_lazy_value(string_with_token: str) -> LazyValue:
    """
    Transforms RawValue (raw string with tokens) to LazyValue (processors and string)
    """
    # tokens_part = re.match(r"(@\w*\s?)+", raw_data)
    # data_part = raw_data
    # converters = []

    # if tokens_part:
    #     data_part = raw_data[tokens_part.end() :]
    #     tokens = tokens_part.group().strip().split(" ")
    #     converters = [get_processor(t) for t in tokens]
    placeholder = get_processor("bypass")
    return LazyValue([placeholder], string_with_token)


def _get_substitution_dependencies(string: str) -> Sequence[TreePath]:
    """Get substitution dependencies, otherwise returns []"""
    ...


def _apply_lazy_processors(lazy_value: LazyValue, context: ContextObject = MISSING):
    """
    Apply processors of @lazy_value using @context and return processed value.
    Assumes outer context won't allow context with missing dependencies.
    """
    context_object = context if not MISSING else ContextObject()
    value = lazy_value.string
    for operator in lazy_value.operators:
        value = operator(value, context_object)
    return value


class DependencyGraph:
    """
    Dependency Graph.
    Responsible ordering/validating dependencies and returning
    nodes in proper order.
    """

    def __init__(self):
        self._graph: TreePathGraph = defaultdict(set)

    def add_edge(self, edge: DependencyEdge):
        """Add node dependency"""
        self._graph[edge.dependent].add(edge.depends_on)

    def add_edges(self, edges: Sequence[DependencyEdge]):
        """Add node dependencies"""
        for edge in edges:
            self.add_edge(edge)

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
