import pytest

from configx.exceptions import MissingContextValue
from configx.services.evaluation.builtin_processors import format_formatter
from configx.services.evaluation.processors_core import build_context_from_dict


@pytest.mark.parametrize(
    "string,ctx_dict,expected",
    [
        pytest.param("hello {this.foo}", {"foo": "world"}, "hello world", id="simple"),
        pytest.param(
            "hello {this.foo.bar}",
            {"foo": {"bar": "world"}},
            "hello world",
            id="nested",
        ),
    ],
)
def test_format_formatter(string, ctx_dict, expected):
    result = format_formatter(raw_string=string, context=ctx_dict)
    assert result == expected


def test_format_formatter_invalid_context():
    """Should raise MissingDependecy with dependencies"""
    string = "hello {missing.dependency}"
    context = {"foo": "world"}
    with pytest.raises(MissingContextValue) as excinfo:
        format_formatter(string, context)

    err = excinfo.value
    assert len(err.dependencies) == 1
    assert err.dependencies == [("missing", "dependency")]
