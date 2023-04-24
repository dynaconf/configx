from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from lib.core.nodes import NodeId
from lib.core.tree import LeafNode, PathNode
from lib.shared.exceptions import LazyValueFound
from lib.shared.types import AllTypes, NodeType, SimpleTypes, TreePath


class InvalidTokenError(Exception):
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


def get_template_variables(string: str):
    """
    Get cleaned template variables from text surrounded by
    single or double curly braces.

    Examples:
        >>> string = "foo { some.variable } bar {{ another.variable }}"
        >>> get_template_variables(string)
        ("some.variable", "another.variable")
    """
    pattern = r"(\{[\w\d\s\.]*\}|\{\{[\w\d\s\.]*\}\})"
    result = re.findall(pattern, string)
    for i, e in enumerate(result):
        result[i] = re.sub(r"[\{|\}]{1,3}", "", e).strip()
    return tuple(result)


def convert_dot_notation_to_tree_path(string: str):
    """
    Converts dot notation string to TreePath object.
    """
    return tuple(string.split("."))


def template_dependencies_in_context(
    template_string: str, context: dict[tuple[str, ...], str]
):
    """
    Checks if template dependencies (text surrounded by single/double curly braces)
    are present in the context, or if there are no dependencies.

    Examples:
        >>> context = {("this", "value"): "world"}
        >>> template_dependencies_in_context("hello { this.value }", context)
        True
        >>> template_dependencies_in_context("hello { this.falsy }", context)
        False
    """
    dependencies = get_template_variables(template_string)
    dependencies = [convert_dot_notation_to_tree_path(e) for e in dependencies]
    try:
        for dep in dependencies:
            context[dep]
        return True
    except KeyError:
        return False


class DependecyStore:
    """
    Data structure responsible for storing and retrieving dependencies in the correct order
    """

    def get_context(self):
        """
        Return the actual context, that is, the currently evaluated dependencies.
        """
        pass


ContextType = dict[TreePath, SimpleTypes]


def apply_converter_chain(
    converter_chain: list[Converter], data: str, context: ContextType
):
    """
    Process data with chain of converters.
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


def validate_token(token_str: str):
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
    converter: Callable[[str, ContextType], Any]
    description: str = ""

    def __call__(self, value, context: ContextType):
        """
        Call to evaluate value
        """
        return self.convert(value, context)

    def convert(self, value, context: ContextType):
        # catch errors to provide better err msg?
        value = self.converter(value, context)
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


def bool_converter(data: str, context: ContextType):
    true_values = ("t", "true", "enabled", "1", "on", "yes", "True")
    return data.lower() in true_values


converters = {
    "str": Converter("str", lambda x, ctx: str(x)),
    "int": Converter("int", lambda x, ctx: int(x)),
    "float": Converter("float", lambda x, ctx: float(x)),
    "bool": Converter("bool", bool_converter),
    "json": Converter("json", lambda x, ctx: json.loads(x)),
    "none": Converter("none", lambda x, ctx: None),
    "format": Converter("format", lambda x, ctx: x),
    "jinja": Converter("jinja", lambda x, ctx: x),
    "lazy": Converter("lazy", lambda x, ctx: x, description="lazy marker"),
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
