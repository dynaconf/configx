import re
from typing import Sequence

from configx.types import TreePath


def get_template_variables(string: str, as_tree_path: bool = False) -> Sequence[str]:
    """
    Get substitution dependencies and strips whitespace.
    If not present returns []

    Examples:
        >>> string = "foo { some.variable } bar {{ another.variable }}"
        >>> get_template_variables(string)
        ["some.variable", "another.variable"]
    """
    pattern = r"\{([^{}]*)\}"
    result = re.findall(pattern, string)
    return [v.strip() for v in result]
