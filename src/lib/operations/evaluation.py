from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable

from lib.core.tree import LeafNode, PathNode
from lib.shared.types import AllTypes, NodeType


class InvalidTokenError(Exception):
    pass


def evaluate_subtree(node: NodeType) -> AllTypes | None:
    """
    Evaluates a node recursively (subtree) into it's corresponding
    python data structure

    Args:
        node: PathNode or LeafNode object

    """
    return _evaluate_first_run(node)


def _evaluate_first_run(node: NodeType) -> AllTypes | None:
    """
    Evaluate raw types (str, int, float, list, dict)
    Cast types
    Analyses evaluation dependencies.
    """
    if isinstance(node, LeafNode):
        return node.setting.raw_data
    elif isinstance(node, PathNode):
        data = None
        if node.type is dict:
            data = {}
            for child in node.children:
                data.update({child.name: _evaluate_first_run(child)})
        elif node.type is list:
            data = []
            for child in node.children:
                data.append(_evaluate_first_run(child))
        return data


def parse_token_symbols(raw_data: str) -> tuple[list[Converter], str]:
    """
    Parse string with token symbols into a converters' chain and a raw data string

    Examples:
        >>> parse_token_symbols("@int 123")
        ([int_converter], "123")

        >>> parse_token_symbols("@int @format {{ this.interpolation}}")
        ([int_converter, format_converter], "{{ this.interpolation}}")
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
    """
    ...


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
    """

    name: str
    converter: Callable[[str], Any]

    def __call__(self, value):
        """
        Call to evaluate value

        Examples:
            >>> c = Converter("int", int)
            >>> c("123")
            123
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
