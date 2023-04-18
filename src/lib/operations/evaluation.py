from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from lib.core.nodes import NodeId
from lib.core.tree import LeafNode, PathNode
from lib.shared.types import AllTypes, NodeType


class InvalidTokenError(Exception):
    pass


class LazyValueFound(Exception):
    pass


def tree_to_dict(node: NodeType, pre_evaluate=False) -> AllTypes | None:
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


def _tree_to_dict(node: NodeType) -> AllTypes | None:
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
    lazy_processor.evaluate_dependencies()
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
            converters, raw = parse_token_symbols(data)
            try:
                data = apply_converter_chain(converters, raw)
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


def parse_token_symbols(raw_data: str) -> tuple[list[Converter], str]:
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


def apply_converter_chain(converter_chain: list[Converter], data: str):
    """
    Process data with chain of converters
    Raises:
        LazyValueFound: if data have dependencies or is marked as lazy
    TODO:
        Implement lazy detection:
            when there is interpolation values (dependencies)
            when data is marked as lazy
    """
    for converter in converter_chain:
        data = converter(data)
    return data


def cast_to_python_type(data, converter: Converter):
    """
    Cast a string to the proper python type, according to the given token.
    """


def validate_token(self, token_str: str):
    """
    Token seting must:
        be string
        begin with @
        be registered
    """
    if not isinstance(token_str, str) and not token_str.startswith("@"):
        raise TypeError(f"Invalid token format (eg. '@token'): {token_str}")
    token_name = token_str[1:]
    if token_name not in converters:
        raise InvalidTokenError(f"Token is not registered: @{token_name}")
    return token_name


@dataclass
class Converter:
    """
    A dynaconf converter token.

    Examples:
        >>> c = Converter("int", int)
        >>> c("123")
        123
    """

    name: str
    converter: Callable[[str], Any]

    def __call__(self, value):
        """
        Call to evaluate value
        """
        return self.convert(value)

    def convert(self, value):
        # catch errors to provide better err msg?
        value = self.converter(value)
        return value


class TokenError(Exception):
    pass


def get_converter(name: str):
    """
    Get registered converters
    TODO add error handling
    """
    name = name[1:] if name.startswith("@") else name
    try:
        converter = converters[name]
    except KeyError:
        raise TokenError(f"The token is not registered: {repr(name)}")
    return converters[name]


converters = {
    "int": Converter("int", int),
    "float": Converter("float", float),
    "bool": Converter("bool", bool),
    "json": Converter("json", json.loads),
    "none": Converter("none", lambda x: None),
    "format": Converter("format", lambda x: x),
    "jinja": Converter("jinja", lambda x: x),
}


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
