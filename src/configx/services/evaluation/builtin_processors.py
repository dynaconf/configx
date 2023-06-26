"""
Builtin processors.
Should contain only builtin implementation of RawProcessors

Name convention is processor_name + _processortype
"""

from typing import Any

import jinja2

from configx.exceptions import MissingContextValue
from configx.services.evaluation.utils import (dict_to_simple_namespace,
                                               dot_str_to_dict_str,
                                               get_template_variables)
from configx.types import MISSING, ContextObject
from configx.utils.tree_utils import str_to_tree_path


def bypass_processor(raw_string: str, context: dict = MISSING) -> Any:
    """Processor that does nothing. May be used as a placeholder."""
    return raw_string


def jinja_formatter(raw_string: str, context: dict):
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    dependencies = get_template_variables(raw_string)
    try:
        return env.from_string(raw_string).render(context)
    except jinja2.exceptions.UndefinedError:
        msg = f"value: {repr(raw_string)} is not available in the context yet."
        dependencies = [str_to_tree_path(s) for s in dependencies]
        raise MissingContextValue(dependencies, msg)


def format_formatter(raw_string: str, context: dict):
    dependencies = get_template_variables(raw_string)
    try:
        # Alternative:
        #   - Could transform {this.foo.bar} to {this['foo']['bar']}
        # dict_string = dot_str_to_dict_str(raw_string)
        # return dict_string.format(this=context)
        object_context = dict_to_simple_namespace(context)
        return raw_string.format(this=object_context)
    except (AttributeError, KeyError):
        msg = f"value: {raw_string!r} is not available in the context"
        dependencies = [str_to_tree_path(s) for s in dependencies]
        raise MissingContextValue(dependencies, msg)


def bash_formatter(raw_string: str, context: dict):
    """
    Interpolate bash variables: $VARIABLE/foo
    """
    ...


def bool_casting(raw_string: str, context: dict):
    true_values = ("t", "true", "enabled", "1", "on", "yes", "True")
    return raw_string.lower() in true_values


def str_casting(raw_string: str, context: dict):
    return str(raw_string)


def int_casting(raw_string: str, context: dict):
    return int(raw_string)


def float_casting(raw_string: str, context: dict):
    return float(raw_string)


def json_casting(raw_string: str, context: dict):
    ...


def none_replacer(raw_string: str, context: dict):
    """Replace string with None"""
    ...


def lazy_marker(raw_string: str, context: dict):
    """Replace string with None"""
    return raw_string


def merge_marker(raw_string: str, context: dict):
    """Replace string with None"""
    return raw_string
