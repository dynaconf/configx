from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from configx.core.setting_tree import Setting, SettingTree
from configx.exceptions import LazyValueFound
from configx.operations.evaluation.converters import Converter, get_converter
from configx.types import PrimitiveTypes, ContextType, NodeId, NodeType


def evaluate():
    pass


def tree_to_dict(node: NodeType, pre_evaluate=False) -> PrimitiveTypes | None:
    """
    Converts a tree to python structure (list and dicts).

    By default, it will not try to evaluate tokens.

    Args:
        node: the root node of the subtree to be converted
        pre_evaluate: should evaluate tree before conversion?

    Raises:
        ???
    """
    if pre_evaluate:
        evaluate_subtree(node)
    return _tree_to_dict(node)


def _tree_to_dict(node: NodeType) -> PrimitiveTypes | None:
    if isinstance(node, LeafNode):
        return node.setting.raw_data
    elif isinstance(node, PathNode):
        data = None
        if node.type is dict:
            data = {}
            for child in node.children:
                data.update({child.name: _tree_to_dict(child)})
        elif node.type is list:
            data = []
            for child in node.children:
                data.append(_tree_to_dict(child))
        return data


def evaluate_subtree(node: NodeType) -> AllTypes | None:
    """
    Evaluates a subtree recursively by mutating it's nodes `evaluated_value` property.

    It performs the following transformations:
        - Values that don't require evalution are bypassed (int, dict, float, etc)
        - Transformations without dependencies are evaluated in the first pass
        - Transformations with dependencies are collected in first pass and
          evaluated in a second pass

    Args:
        node: PathNode or LeafNode object

    Notes:
        - Not sure if should or not mutate. I guess mutating will do no harm here.

    """
    lazy_processor = LazyProcessor()
    _evaluate_first_pass(node, lazy_processor)
    # lazy_processor.evaluate_dependencies()
    return


def _evaluate_first_pass(
    node: NodeType, lazy_processor: LazyProcessor
) -> AllTypes | None:
    """
    Evaluate raw types and Tokens with no dependencies into nodes
    and adds lazy values to lazy_processor (by mutatation)

    Notes:
        - This would be more elegant with match case, but this would
          break compatipability with python<3.10

    TODO:
        Make this mutate nodes instead of rendering dict/lists
        Add new proper tests for this
    """
    if isinstance(node, LeafNode):
        data = node.setting.raw_data
        node_id = node.identifier
        if isinstance(data, str):
            converters, raw = _parse_token_symbols(data)
            try:
                data = _apply_converter_chain(converters, raw, {})
            except LazyValueFound:
                lazy_value = LazyValue(node_id, raw, converters)
                lazy_processor.add(lazy_value)

        return data
    elif isinstance(node, PathNode):
        data = None
        if node.type is dict:
            data = {}
            for child in node.children:
                data.update({child.name: _evaluate_first_pass(child, lazy_processor)})
        elif node.type is list:
            data = []
            for child in node.children:
                data.append(_evaluate_first_pass(child, lazy_processor))
        return data


def _parse_token_symbols(raw_data: str) -> tuple[list[Converter], str]:
    """
    Parse string with token symbols into a converters' chain and a raw data string

    Examples:
        >>> parse_token_symbols("@int 123")
        ([int_converter], "123")

        >>> parse_token_symbols("@int @format {{ this.interpolation}}")
        ([int_converter, format_converter], "{{ this.interpolation}}")

    Notes:
        Should raise or bypass if there are not tokens?
    """
    tokens_part = re.match(r"(@\w*\s?)+", raw_data)
    data_part = raw_data
    converters = []

    if tokens_part:
        data_part = raw_data[tokens_part.end() :]
        tokens = tokens_part.group().strip().split(" ")
        converters = [get_converter(t) for t in tokens]
    return converters, data_part


def _apply_converter_chain(
    converter_chain: Sequence[Converter], data: str, context: ContextType
):
    """
    Process data with chain of converters from index 0 to n.
    If a Converter raises LazyValueFound, the process is stopped.

    Raises:
        LazyValueFound: when
            - template value is not found in context
            - lazy converter is present
    """
    try:
        for converter in converter_chain:
            data = converter(data, context)
    except LazyValueFound:
        raise

    return data


# class DependecyStore:
#     """
#     Data structure responsible for storing and retrieving dependencies in the correct order
#     """

#     def get_context(self):
#         """
#         Return the actual context, that is, the currently evaluated dependencies.
#         """
#         pass


@dataclass
class LazyValue:
    """
    Object that holds relevant data to evaluate itself
    """

    id: NodeId
    raw: str
    converters: list[Converter]
    dependencies: list[str] | None = None


class LazyProcessor:
    """
    Responsible for collecting LazyValues, analysing and storing their dependencies
    and evaluating them in the correct order.

    Examples: TODO
        >>> l = LazyProcessor()
        >>> l.add(LazyValue(""))
        >>> l.add(LazyValue(""))
        >>> l.add(LazyValue(""))
    """

    def __init__(self):
        self._conatainer = []

    def add(self, lazy_value: LazyValue):
        """
        Adds a lazy_value to the internal data structure.

        TODO implement properly, first with queue
        (which should be easier than graph)
        """
        self._conatainer.append(lazy_value)

    def evaluate_dependencies(self):
        """
        Evaluate lazy values in the proper order
        """
