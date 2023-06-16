import pytest

from configx.exceptions import MissingContextValue
from configx.services.evaluation.builtin_processors import format_formatter
from configx.services.evaluation.processors_core import build_context_from_dict
from configx.types import DependencyEdge
from configx.utils.evaluation_utils import get_template_variables


@pytest.mark.parametrize(
    "input, expected",
    [
        ("hello {world} foo", ["world"]),
        ("hello { world } foo", ["world"]),
        ("hello {{world}} foo", ["world"]),
        ("hello {{ world }} foo", ["world"]),
        ("hello {world} foo {bar}{spam}", ["world", "bar", "spam"]),
        ("hello {{ {world} }} foo", ["world"]),
        # TODO support this
        # (r"hello {{ \{world\} }} foo", ["{world}"]),
        # ("hello {{{ world }}} foo", ["{ world }"]),
    ],
)
def test_get_template_variables(input, expected):
    result = get_template_variables(input)
    assert result == expected


@pytest.mark.parametrize(
    "string,ctx_dict,expected",
    [
        ("hello {this.foo}", {"foo": "world"}, "hello world"),
        ("hello {this.foo.bar}", {"foo": {"bar": "world"}}, "hello_world"),
    ],
)
def test_format_formatter(string, ctx_dict, expected):
    context = build_context_from_dict(ctx_dict)
    result = format_formatter(string, context)
    assert result == expected


def test_format_formatter_invalid_context():
    """Should raise MissingDependecy with dependencies"""
    string = "hello {missing.dependency}"
    context = build_context_from_dict({"foo": "world"})
    with pytest.raises(MissingContextValue) as excinfo:
        format_formatter(string, context)

    err = excinfo.value
    assert len(err.dependencies) == 1
    assert err.dependencies == [("missing", "dependency")]
