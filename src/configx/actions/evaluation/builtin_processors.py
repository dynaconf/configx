"""
Builtin processors.
Should contain only builtin implementation of RawProcessors

Name convention is processor_name + _processortype
"""

from typing import Any

import jinja2

from configx.exceptions import MissingContextValue
from configx.types import MISSING, ContextObject


def bypass_processor(raw_string: str, context: ContextObject = MISSING) -> Any:
    """Processor that does nothing. May be used as a placeholder."""
    return raw_string


def jinja_formatter(raw_string: str, context: ContextObject):
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    try:
        return env.from_string(raw_string).render(context)
    except jinja2.exceptions.UndefinedError:
        raise MissingContextValue(
            f"value: {repr(raw_string)} is not available in the context yet."
        )


def format_formatter(raw_string: str, context: dict):
    try:
        return raw_string.format(context)
    except KeyError:
        raise MissingContextValue(
            f"value: {repr(raw_string)} is not available in the context yet."
        )


def bash_formatter(raw_string: str, context: ContextObject):
    """
    Interpolate bash variables: $VARIABLE/foo
    """
    ...


def bool_casting(raw_string: str, context: ContextObject):
    true_values = ("t", "true", "enabled", "1", "on", "yes", "True")
    return raw_string.lower() in true_values


def str_casting(raw_string: str, context: ContextObject):
    return str(raw_string)


def int_casting(raw_string: str, context: ContextObject):
    return int(raw_string)


def float_casting(raw_string: str, context: ContextObject):
    return float(raw_string)


def json_casting(raw_string: str, context: ContextObject):
    ...


def none_replacer(raw_string: str, context: ContextObject):
    """Replace string with None"""
    ...


def lazy_marker(raw_string: str, context: ContextObject):
    """Replace string with None"""
    return raw_string


def merge_marker(raw_string: str, context: ContextObject):
    """Replace string with None"""
    return raw_string
