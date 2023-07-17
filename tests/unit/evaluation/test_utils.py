import pytest

from configx.exceptions import TokenError
from configx.services.evaluation.utils import (
    _parse_raw_value_tokens,
    dict_to_simple_namespace,
    get_template_variables,
)

pytestmark = pytest.mark.utils


@pytest.mark.parametrize(
    "input, expected",
    [
        ("hello {world} foo", [("world",)]),
        ("hello { world } foo", [("world",)]),
        ("hello {{world}} foo", [("world",)]),
        ("hello {{ world }} foo", [("world",)]),
        ("hello {world} foo {bar}{spam}", [("world",), ("bar",), ("spam",)]),
        ("hello {{ {world} }} foo", [("world",)]),
        # TODO support this
        # (r"hello {{ \{world\} }} foo", ["{world}"]),
        # ("hello {{{ world }}} foo", ["{ world }"]),
    ],
)
def test_get_template_variables(input, expected):
    result = get_template_variables(input)
    assert result == expected


@pytest.mark.parametrize(
    "input, expected",
    [
        ("hello {this} foo", []),
        ("hello {this.world} foo", [("world",)]),
        (
            "hello {this.world} foo {this.bar}{this.spam}",
            [("world",), ("bar",), ("spam",)],
        ),
    ],
)
def test_get_template_variables_with_ignore_flag(input, expected):
    result = get_template_variables(input, ignore_first_node=True)
    assert result == expected


@pytest.mark.parametrize(
    "raw_value,expected_tokens, expeted_string",
    (
        ("@a", ("a",), ""),
        ("@@", ("@",), ""),
        ("@foo @ bar", ("foo",), "@ bar"),
        ("@foo @bar eggs", ("foo", "bar"), "eggs"),
        ("@foo spam @eggs", ("foo",), "spam @eggs"),
        ("@foo  spam", ("foo",), " spam"),
        ("@foo   @spam   eggs", ("foo", "spam"), "  eggs"),
    ),
)
def test_parse_raw_value_tokens(raw_value, expected_tokens, expeted_string):
    token_names, string = _parse_raw_value_tokens(raw_value)
    assert token_names == expected_tokens
    assert string == expeted_string


@pytest.mark.parametrize("raw_value", ("@", "@ foo"))
def test_parse_raw_value_tokens_raises(raw_value):
    with pytest.raises(TokenError):
        _parse_raw_value_tokens(raw_value)


def test_dict_to_simple_namespace():
    dict_data = {"foo": {"bar": "world"}, "listy": ["a", "b", "c"]}
    this = dict_to_simple_namespace(dict_data)
    assert this.foo.bar
    assert this.foo.bar == "world"
    assert this.listy._1 == "b"
