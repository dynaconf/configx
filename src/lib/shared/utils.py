import re

from lib.shared.types import CompoundTypes, TreePath


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


def convert_dot_notation_to_tree_path(string: str):
    """
    Converts dot notation string to TreePath object.
    """
    return tuple(string.split("."))


def convert_tree_path_to_dot_notation(tree_path: TreePath):
    """
    Converts a TreePath object to dot notation string.
    """
    return ".".join(tree_path)


def convert_context_type_to_dot_syntax(tree_path: TreePath):
    """
    Converts from ContextType (dict with TreePath as keys)
    to dot notation syntax (dot-notation string as keys)
    """
    pass


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
