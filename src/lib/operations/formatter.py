"""
Formatters are converter function that take string values, a context for variable
interpolation and raise LazyValueFound some context variable is missing.

TODO change the exception name
"""
import jinja2

from lib.shared.exceptions import LazyValueFound


def jinja_formatter(value: str, context: dict):
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    try:
        return env.from_string(value).render(**context)
    except jinja2.exceptions.UndefinedError:
        raise LazyValueFound


def python_formatter(value: str, context: dict):
    try:
        return value.format(**context)
    except KeyError:
        raise LazyValueFound


def bash_formatter(value: str, context: dict):
    """
    Interpolate bash variables: $VARIABLE/foo
    """
