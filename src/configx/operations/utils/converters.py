"""
Formatters are converter functions that take string values, a context for variable
interpolation and raise LazyValueFound some context variable is missing.

TODO change the exception name
"""
from dataclasses import dataclass
from typing import Any, Callable
import json

import jinja2

from configx.exceptions import LazyValueFound, TokenError
from configx.utils import convert_dot_notation_to_tree_path, get_template_variables

ContextType = dict


def jinja_formatter(value: str, context: dict):
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    try:
        return env.from_string(value).render(**context)
    except jinja2.exceptions.UndefinedError:
        raise LazyValueFound(
            f"value: {repr(value)} is not available in the context yet."
        )


def python_formatter(value: str, context: dict):
    try:
        # pre-format context to use SimpleNamespaces
        # context = dict_to_simple_namespace(context)
        return value.format(**context)
    except KeyError:
        raise LazyValueFound(
            f"value: {repr(value)} is not available in the context yet."
        )


def bash_formatter(value: str, context: dict):
    """
    Interpolate bash variables: $VARIABLE/foo
    """


def bool_converter(data: str, context: ContextType):
    true_values = ("t", "true", "enabled", "1", "on", "yes", "True")
    return data.lower() in true_values


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


def add_converter():
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
    "str": Converter("str", lambda x, ctx: str(x)),
    "int": Converter("int", lambda x, ctx: int(x)),
    "float": Converter("float", lambda x, ctx: float(x)),
    "bool": Converter("bool", bool_converter),
    "json": Converter("json", lambda x, ctx: json.loads(x)),
    "none": Converter("none", lambda x, ctx: None),
    "format": Converter("format", python_formatter),
    "jinja": Converter("jinja", jinja_formatter),
    "lazy": Converter("lazy", lambda x, ctx: x, description="lazy marker"),
}
