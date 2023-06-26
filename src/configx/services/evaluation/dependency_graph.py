from configx.types import DependencyEdge, TreePath, TreePathGraph


from collections import defaultdict
from graphlib import TopologicalSorter
from typing import Any, Generator, Sequence


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