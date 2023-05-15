import pytest

from lib.core.tree import Tree
from lib.operations.evaluation import (
    _apply_converter_chain,
    _parse_token_symbols,
    evaluate_subtree,
    get_converter,
    tree_to_dict,
)
from lib.shared.exceptions import TokenError
from lib.shared.utils import (
    convert_dot_notation_to_tree_path,
    get_template_variables,
    template_dependencies_in_context,
)

# from lib.operations.evaluation import evaluate_subtree


def test_convert_dot_notation_to_tree_object():
    """
    Should convert foo.bar.spam to ('foo', 'bar', 'spam')
    """
    c = convert_dot_notation_to_tree_path

    assert c("foo") == ("foo",)
    assert c("foo.bar") == ("foo", "bar")
    assert c(".foo.bar") == ("", "foo", "bar")


def test_get_template_variables():
    """
    Should
        template variables from string template
    When
        between single or double coursly braces {} or {{}}
    """
    c = get_template_variables

    assert c("foo bar") == ()
    assert c("foo {bar}") == ("bar",)
    assert c("{bar} foo") == ("bar",)
    assert c("foo {{ bar }}") == ("bar",)
    assert c("foo {bar} spam {{eggs}}") == ("bar", "eggs")
    assert c("foo {{bar} spam {eggs}}") == ("bar", "eggs")
    assert c("foo { bar.spam }") == ("bar.spam",)


@pytest.mark.parametrize(
    "raw_data,expected",
    (
        pytest.param("no-tokens", ([], "no-tokens"), id="none-value"),
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
    Should perform the following conversion:
    "@mytoken data" -> ([mytoken-transformer], 'data')
    "@int @mytoken data" -> ([int-transformer, mytoken-transformer], 'data')
    """
    converter_stack, data = _parse_token_symbols(raw_data)
    assert converter_stack == expected[0]
    assert data == expected[1]


def test_parse_token_symbols_raises():
    """
    Should raise on invalid tokens
    """
    with pytest.raises(TokenError):
        _parse_token_symbols("@unknown data")

    with pytest.raises(TokenError):
        _parse_token_symbols("@int @unknown data")


@pytest.mark.parametrize(
    "data",
    (
        pytest.param("Hello this.foo", id="no-deps"),
        pytest.param("Hello { this.foo }", id="one-value-single-curly"),
        pytest.param("Hello {{ this.foo }}", id="one-value-double-curly"),
        pytest.param("Hello { this.foo } { this.bar }", id="two-values-single-curly"),
        pytest.param(
            "Hello {{ this.foo }} {{ this.bar }}", id="two-values-double-curly"
        ),
    ),
)
def test_template_dependencies_in_context_is_true(data):
    """
    When context contains data dependencies: {{ dep }} or { dep }
    Should return True
    """
    context = {("this", "foo"): 123, ("this", "bar"): [1, 2, 3]}
    assert template_dependencies_in_context(data, context) is True


def test_template_dependencies_in_context_is_false():
    """
    When context does not contain data dependencies: {{ dep }} or { dep }
    Should return False
    """
    fn = template_dependencies_in_context
    context = {("this", "foo"): 123, ("this", "bar"): [1, 2, 3]}

    assert fn("template {{ this.foobar }}", context) is False
    assert fn("{ this.bars} template", context) is False


@pytest.mark.parametrize(
    "converter_name, input, output",
    (
        pytest.param("int", "123", 123, id="int"),
        pytest.param("float", "12.3", 12.3, id="float"),
        pytest.param("str", 123, "123", id="str"),
        pytest.param("bool", "true", True, id="bool-true-lower"),
        pytest.param("bool", "TrUe", True, id="bool-true-mixed"),
        pytest.param("bool", "False", False, id="bool-false-lower"),
        pytest.param("bool", "bar", False, id="bool-false-random"),
    ),
)
def test_builtin_converters_without_template_variables(converter_name, input, output):
    """
    Should apply converter correctly
    """
    converter = get_converter(converter_name)
    result = converter(input, {})
    assert result == output


@pytest.mark.parametrize(
    "converter_name, input, output",
    (
        pytest.param("format", "hello {value}", "hello world", id="format-one"),
        pytest.param(
            "format", "hello {foo.bar}", "hello 123", id="format-nested"
        ),
        pytest.param("jinja", "hello {{ value }}", "hello world", id="jinja-one"),
        # pytest.param("format", "12.3", 12.3, id="float"),
        # pytest.param("jinja", 123, "123", id="str"),
        # pytest.param("jinja", 123, "123", id="str"),
    ),
)
def test_builtin_formatters_with_template_variables_in_context(
    converter_name, input, output
):
    context = {"value": "world", "foo": {"bar": 123}}

    converter = get_converter(converter_name)
    result = converter(input, context)
    assert result == output


def test_builtin_formatters_with_template_variables_not_in_context():
    pass


@pytest.mark.parametrize(
    "converters, input, output",
    (
        pytest.param(("int",), "123", 123, id="int"),
        pytest.param(("int", "str"), "12", "12", id="int-str"),
        pytest.param(("float", "int"), "12.3", 12, id="float-int"),
        pytest.param(("int", "float"), "12", 12.0, id="int-float"),
    ),
)
def test_apply_converter_chain_without_template_variables(converters, input, output):
    """
    When
        not using formatters @jinja and @format
    Should apply converters ()
    """
    converters = [get_converter(e) for e in converters]
    result = _apply_converter_chain(converters, input, context={})
    assert result == output


@pytest.mark.parametrize(
    "converters, input, output",
    (
        pytest.param(("int",), "123", 123, id="int"),
        pytest.param(("int", "str"), "12", "12", id="int-str"),
        pytest.param(("float", "int"), "12.3", 12, id="float-int"),
        pytest.param(("int", "float"), "12", 12.0, id="int-float"),
    ),
)
def test_apply_converter_chain_with_template_variables_in_context(
    converters, input, output
):
    """
    When
        using formatters @jinja and @format
        template variables are in context
    Should substitute variables variables correctly
    """


@pytest.mark.parametrize(
    "converters, input, output",
    (
        pytest.param(("int",), "123", 123, id="int"),
        pytest.param(("int", "str"), "12", "12", id="int-str"),
        pytest.param(("float", "int"), "12.3", 12, id="float-int"),
        pytest.param(("int", "float"), "12", 12.0, id="int-float"),
    ),
)
def test_apply_converter_chain_with_template_variables_not_in_context(
    converters, input, output
):
    """
    When
        using formatters @jinja and @format
        template variables are not in context
    Should raise LazyValueFound
    """


# evaluating


def test_tree_to_dict_flat():
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

    result = tree_to_dict(t.root)
    assert isinstance(result, dict)
    assert result["str_node"] == "value"
    assert result["int_node"] == 123
    assert result["float_node"] == 1.23


def test_tree_to_dict_nested():
    """
    When
        tree has multiple levels
        tree has only raw types
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

    result = tree_to_dict(t.root)
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
def test_evaluate_single_casting_token_without_lazy_values(raw_data, evaluated):
    """
    When
        Tree has casting tokens
        Tree hasn't lazy tokens (which require evaluation dependencies)
    Should convert to the correct type
    """


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
