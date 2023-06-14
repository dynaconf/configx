import re


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