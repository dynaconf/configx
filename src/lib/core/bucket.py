from typing import TYPE_CHECKING, Any, Literal, NamedTuple, OrderedDict, Sequence

from lib.shared.types import Children, DataSource, Environment, NodeType

if TYPE_CHECKING:
    from lib.core.nodes import BaseNode, LeafNode, NodeId, PathNode
else:
    NodeId = object
    BaseNode = object
    LeafNode = object
    PathNode = object


def main():
    pos = PositionalDict()
    pos.update({"foo": "bar", "spam": "eggs", "blabla": 123})
    print(pos)


class Bucket:
    """
    The container for Nodes and Leaves

    Responsible for holding and efficiently acessing
    Node and Leaf objects.
    """

    def __init__(
        self, initial_nodes: Children | None = None, owner: NodeType | None = None
    ):
        # initializes with optional initial list of nodes
        initial_data = []
        if initial_nodes:
            initial_data = [(n, n) for n in initial_nodes]
        self.__container = PositionalDict(initial_data)

        # Optionally provide the owner Node, for convenience
        self.owner = owner

    # Crud

    def append(self, node: NodeType):
        """
        Append item to the last position

        rules:
        - if one PathNode named 'foo' is present,
          a LeaveNode named 'foo' will override it
        - if one or more LeavNodes named 'foo' are present
          appending a PathNode named 'foo' will override all of them
        """
        self.__container[node.identifier] = node

    def get_by_props(
        self,
        name: str,
        env: Environment | None = None,
        source: DataSource | None = None,
    ) -> list[NodeType]:
        """
        Get nodes by properties
        Runs in O(n)

        TODO implement env and data_source filters
        """
        return [n for n in self if n.name == name]

    def get_by_id(self, node_id: NodeId) -> list[NodeType]:
        """
        Get one node by a NodeId
        Runs in O(1)
        """
        return self.__container[node_id]

    def get_by_index(self, index: int) -> BaseNode:
        """
        Get one node by an index
        Runs in O(1)
        """
        return self.__container[index]

    def remove_by_node_id(self, node_id: NodeId) -> NodeType:
        """
        Remove node from bucket by it's @node_id and return it
        """
        self.__container.move_to_end(node_id)
        _, node = self.__container.popitem()
        return node

    # Iterators

    def iter(self, type: Literal["leaf", "path"] | None = None):
        """
        Return Generator with all nodes

        If @type is given, filter by this tag.
        """
        if type == "leaf":
            return (n for n in self if isinstance(n, LeafNode))
        if type == "path":
            return (n for n in self if isinstance(n, PathNode))
        return self

    def inspect(self, verbose=0, relative_path=True):
        """
        Utility to inspect bucket data
        TODO see lib to pretty print these stuff
        """
        print("=" * 10)
        print(f"parent: {self.owner}")
        print(f"path: {self.owner.get_identifier() if self.owner else None}")
        print(f"length: {self.__len__()}")
        print("=" * 10)

        for i, n in enumerate(self):
            print(f"[{i}] {n}")

    # Dunder

    def __len__(self):
        return len(self.__container)

    def __iter__(self):
        yield from self.__container.values()

    def __str__(self):
        return "\n".join(str(n) for n in self)

    def __delitem__(self, key: int | NodeType):
        """
        del B[i]
        del B[BucketItem]
        """

    def __getitem__(self, key):
        return self.__container.__getitem__(key)


class PositionalDict(OrderedDict):
    """
    Data Structure to hold Node and Leaf by key and index

    It will use a name for hash-based lookup or
    a positional index.

    Notes on Current implemenation

        - has index lookup in O(n). This can be improved by holding data
        in both list and dict, but should use more memory.

        - for handling key-duplicates, it will require a Key object
        that will account for uniquness.

        This will be fast for queries of a specific Setting/Env/Src,
        but it may need optimizations for retriving partial queries.
        (which do not include all name/env/source)

    """

    def __getitem__(self, key):
        """
        Support for indexable search
        """
        if isinstance(key, slice):
            raise TypeError("slices are not supported yet")

        if isinstance(key, int):
            # support for negative index
            if key < 0:
                key = len(self) + key

            # range check
            if key >= len(self) or key < 0:
                raise IndexError()

            # get node in O(n)
            for index, node in enumerate(self.values()):
                if index == key:
                    return node

        return super().__getitem__(key)


if __name__ == "__main__":
    exit(main())
