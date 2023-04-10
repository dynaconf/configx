import pytest
from attr import converters

from lib.core.tree import Tree
from lib.operations.evaluation import (
    evaluate_subtree,
    get_converter,
    parse_token_symbols,
    TokenError
)

# from lib.operations.evaluation import evaluate_subtree


@pytest.mark.parametrize(
    "raw_data,expected",
    (
        pytest.param("@none", ([get_converter("none")], ""), id="none-value"),
        pytest.param("@int 123", ([get_converter("int")], "123"), id="simple-int"),
        pytest.param("@bool 123", ([get_converter("bool")], "123"), id="simple-bool"),
        pytest.param(
            "@float 123", ([get_converter("float")], "123"), id="simple-float"
        ),
        pytest.param("@json 123", ([get_converter("json")], "123"), id="simple-json"),
        pytest.param(
            "@format 123", ([get_converter("format")], "123"), id="simple-format"
        ),
        pytest.param(
            "@int @format 123",
            ([get_converter("int"), get_converter("format")], "123"),
            id="compound format",
        ),
    ),
)
def test_parse_token_symbols(raw_data, expected):
    """
    Should perform the following transformations:
    "@mytoken data" -> ([token_transformer], 'data')
    """
    converter_stack, data = parse_token_symbols(raw_data)
    assert converter_stack == expected[0]
    assert data == expected[1]


def test_parse_token_symbols_raises():
    """
    Should raise on invalid tokens
    """
    with pytest.raises(TokenError):
        parse_token_symbols("@unknown data")

    with pytest.raises(TokenError):
        parse_token_symbols("@int @unknown data")


# evaluating


def test_evaluate_raw_types_with_one_level():
    """
    When
        tree has one level
        tree has only raw types (bypass @tokens)
    Should return the correct python data structure
    """
    t = Tree()
    t.create_node("str_node", "value")
    t.create_node("int_node", 123)
    t.create_node("float_node", 1.23)

    result = evaluate_subtree(t.root)
    assert isinstance(result, dict)
    assert result["str_node"] == "value"
    assert result["int_node"] == 123
    assert result["float_node"] == 1.23


def test_evaluate_raw_types_with_nested_levels():
    """
    When
        tree has multiple levels
        tree has only raw types (bypass @tokens)
    Should return the correct python data structure
    """
    t = Tree()
    t.create_node(
        "nesting_a",
        {
            "str_node": "value",
            "int_node": 123,
            "float_node": 1.23,
            "list_node": ["a", "b", "c"],
        },
    )
    t.create_node("nesting_b", [1, 2, 3, {"foo": "bar"}])

    result = evaluate_subtree(t.root)
    assert isinstance(result, dict)
    assert result["nesting_a"]["str_node"] == "value"
    assert result["nesting_a"]["int_node"] == 123
    assert result["nesting_a"]["float_node"] == 1.23
    assert result["nesting_a"]["list_node"] == ["a", "b", "c"]
    assert result["nesting_b"][0] == 1
    assert result["nesting_b"][1] == 2
    assert result["nesting_b"][2] == 3
    assert result["nesting_b"][3] == {"foo": "bar"}


@pytest.mark.parametrize(
    "raw_data,evaluated",
    (
        pytest.param("@int 123", 123, id="integer-casting"),
        pytest.param("@float 1.23", 1.23, id="float-casting"),
        # pytest.param("@list []", 123, id="list-casting"),
        # pytest.param("@dict {}", 123, id="dict-casting"),
    ),
)
def test_evaluate_one_casting_token_without_lazy_values(raw_data, evaluated):
    """
    When
        Tree has casting tokens
        Tree hasn't lazy tokens (which require evaluation dependencies)
    Should convert to the correct type
    """
    t = Tree()
    t.create_node("value", raw_data)
    result = evaluate_subtree(t.root)
    assert isinstance(result, dict)
    assert result["value"] == evaluated


def test_evaluate_chained_casting_token_without_lazy_values():
    """
    When
        Tree has casting tokens
        Tree hasn't lazy tokens (which require evaluation dependencies)
    Should convert to the correct type
    """


def test_evaluate_casting_tokens_with_lazy_values_bypasses_type_casting():
    """
    When
        Tree has casting tokens
        Tree hasn't interpolation tokens
    Should bypass (will be handled lazy)
    """
