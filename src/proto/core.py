"""
Minimal dynaconf program data flow.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence, Type, TypedDict, Union


def main():
    ...


# Core


def ingest_data(data, mark_parser: Optional[MarkupParser] = None) -> Node:
    """Transforms data into a tree"""
    raise NotImplementedError()


def merge_tree(original: Node, other: Node) -> Sequence[DataPatch]:
    """Merge tree rooted at @original with newer tree rooted at @other.

    Returns DataPatches, which may be used to patch dict-data-structs.
    """
    raise NotImplementedError()


def split_mixed_tree(root: Node) -> tuple[Node, Node]:
    """Split MixedTree (that contains both Elements and Components nodes) into
    ElementTree and Component tree.
    """
    raise NotImplementedError


def evaluate_component_tree(root: Node, context: dict) -> Node:
    """Transform ComponentTree into ElementTree"""
    raise NotImplementedError


def reconcile_data(
    data: dict,
    tree: Node,
    data_patches: Optional[Sequence[DataPatch]] = None,
    use_patch: bool = False,
) -> None:
    """Update data with Tree"""
    raise NotImplementedError()


# Auxiliary functions


def diff_tree(original: Node, other: Node) -> TreePatch:
    """Diff tree nodes recursively and generate NodePatch"""
    raise NotImplementedError()


def patch_tree(patches: Sequence[TreePatch], tree: Node) -> DataPatch:
    """Apply NodePatches to tree and return DataPatch."""
    raise NotImplementedError()


def render_tree(root: Node) -> dict:
    raise NotImplementedError()


def patch_data(patches: Sequence[DataPatch], data: dict) -> DataPatch:
    """Apply NodePatches to tree and return DataPatch."""
    raise NotImplementedError()


# Auxiliary classes


class TreePatch:
    """Patch to be applied into a tree."""


class DataPatch:
    """Patch to be applied into a dict-data."""


# Dependency Injection


class MergeInterpreter:
    """Interprets TreePatch and Node metadata and return merge action."""


class MarkupParser:
    """Parses markup inside dict-data-structures and returns tuple of
    cleaned up data and proper markup names.

    Example:
        >>> data = {"dynaconf_merge": True, "A": "a"}
        >>> markup_parser = MarkupParser()
        >>> markup_parser.parse(data)
        ({"A", "a"}, {"merge_node": True})
    """

    def parse(self, data: dict) -> tuple[dict, dict]:
        raise NotImplementedError()


# Node


class DictElement:
    ...


class ListElement:
    ...


class ValueElement:
    ...


NodeType = Union[
    Type[DictElement],
    Type[ListElement],
    Type[ValueElement],
]


NonContainerType = Union[str, int, bool, float]


class NodeProps(TypedDict, total=False):
    full_path: tuple[str]
    merging_marks: list[str]
    merging_strategy: str


@dataclass(frozen=True)
class Node:
    # hashable
    node_type: NodeType = field(compare=True, hash=True)
    key: str = field(compare=True, hash=True)
    value: Optional[NonContainerType] = field(compare=True, default=None, hash=True)

    # non-hashable
    children: tuple[Node, ...] = field(
        compare=False, repr=False, default_factory=tuple
    )  # type: ignore
    props: NodeProps = field(
        compare=False, repr=True, default_factory=dict  # type: ignore
    )


if __name__ == "__main__":
    ...
