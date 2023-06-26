"""
General utilities. These should probably be more specific.
"""
import re

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


def print_header(title: str, substitle: str = ""):
    div = "=" * (len(title) + 4)
    print()
    print(div)
    print("=", title, "=")
    print(div)
    if substitle:
        print(substitle)
    print()

