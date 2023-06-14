"""
General utilities. These should probably be more specific.
"""
import re
from types import SimpleNamespace

from configx.types import CompoundTypes


def normalize_compound_type(compound: CompoundTypes):
    """
    Transform list to a dict-form by setting index as keys.
    Bypasses if already dict

    Returns:
        tuple(node_type, dict_data)

    Eg. `['foo', 'bar'] -> {'0':'foo', 1:'bar'}`
    """
    if isinstance(compound, list):
        new_form = {}
        for i, e in enumerate(compound):
            new_form[str(i)] = e
        return (list, new_form)
    return (dict, compound)


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


def dict_to_simple_namespace(data: dict):
    """
    Transforms a dict into a SimpleNamespace object with dot notation access.
    """
    obj = SimpleNamespace()
    _dict_to_simple_namespace(data, obj)
    return obj


def _dict_to_simple_namespace(data: dict, obj: SimpleNamespace, path: str = ""):
    """
    Recursive function to add dict entries as SimpleNamespaces into obj.
    """
    if isinstance(data, dict):
        for k, v in data.items():
            obj.__setattr__(k, v)
            if isinstance(v, dict):
                _dict_to_simple_namespace(v, obj)
    return data


def print_header(title: str, substitle: str = ""):
    div = "=" * (len(title) + 4)
    print()
    print(div)
    print("=", title, "=")
    print(div)
    if substitle:
        print(substitle)
    print()

