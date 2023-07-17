import re
from types import SimpleNamespace
from typing import Any, Sequence

from configx.exceptions import TokenError
from configx.types import MISSING, ContextObject, LazyValue, TreePath
from configx.utils.tree_utils import str_to_tree_path


def get_template_variables(
    string: str, ignore_first_node: bool = False
) -> Sequence[TreePath]:
    """
    Get substitution dependencies as TreePaths.
    If not present returns []

    Examples:
        >>> string = "foo { some.variable } bar {{ another.variable }}"
        >>> get_template_variables(string)
        ["some.variable", "another.variable"]
    """
    pattern = r"\{([^{}]*)\}"
    paths = re.findall(pattern, string)
    result = []
    for path_str in paths:
        path = str_to_tree_path(path_str.strip())
        if ignore_first_node:
            if not len(path) > 1:
                continue
            result.append(path[1:])
        else:
            result.append(path)
    return result


def _parse_raw_value_tokens(raw_value: str) -> tuple[tuple[str, ...], str]:
    """
    Parses raw_value and return tuple of token-names and string.
    - Ignores whitespace between tokens
    - After last token, ignores one whitespace and capture remaining.
    Eg: "@foo @bar spam" -> (('foo', 'bar'), 'spam')
    """
    if not raw_value.startswith("@") or len(raw_value) < 2:
        raise TokenError("No token found in string")

    token_names = []
    string_word = ""
    i = 0
    start = 0
    end = 0
    while i < len(raw_value) - 1:
        if raw_value[i] == "@":
            start = end = i + 1
            while end < len(raw_value) and not raw_value[end].isspace():
                end += 1
            token_names.append(raw_value[start:end])
            i = end + 1
        elif raw_value[i].isspace():
            i += 1
        else:
            string_word = raw_value[end + 1 :]
            break
    return tuple(token_names), string_word


def _apply_lazy_processors(lazy_value: LazyValue, context: ContextObject = MISSING):
    """
    Apply processors of @lazy_value using @context and return processed value.
    May raise MissingContextValue with the missing dependencies (inside err.dependencies).
    """
    context_object = context if not MISSING else {}
    value = lazy_value.string
    for operator in reversed(lazy_value.operators):
        value = operator(value, context_object)
    return value


def dict_to_simple_namespace(dict_data: dict):
    """
    Transforms a dict into a SimpleNamespace object with dot notation access.
    """

    def recurse(d: dict | Any):
        if isinstance(d, dict):
            obj = SimpleNamespace()
            for k, v in d.items():
                setattr(obj, k, recurse(v))
            return obj
        elif isinstance(d, list):
            obj = SimpleNamespace()
            for k, v in enumerate(d):
                setattr(obj, "_{}".format(str(k)), recurse(v))
            return obj
        else:
            return d

    return recurse(dict_data)


def dot_str_to_dict_str(string: str) -> str:
    """
    Transform dot path string to dict access string

    Example:
        >>> dot_str_to_dict_str("foo.bar.spam")
        "foo['bar']['spam']
    """
    ...
