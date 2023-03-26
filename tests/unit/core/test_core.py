import pytest

from lib.core.tree import PositionalDict

params__positional_dict__initial = (
    pytest.param([("foo", 1)], id="one-element"),
    pytest.param([("foo", 1), ("bar", 2), ("baz", 3)], id="multiple-element"),
)


@pytest.mark.parametrize("initial", params__positional_dict__initial)
def test_positional_dict__init(initial):
    p = PositionalDict(initial)

    assert len(p) == len(initial)
    for i, value in enumerate(initial):
        k, v = value
        assert p[k] == v
        assert p[i] == v


@pytest.mark.parametrize("initial", params__positional_dict__initial)
def test_positional_dict__set_one_by_one(initial):
    p = PositionalDict()
    for k, v in initial:
        p[k] = v

    assert len(p) == len(initial)
    for i, value in enumerate(initial):
        k, v = value
        assert p[k] == v
        assert p[i] == v


def test_positional_dict__init_repeated_elements():
    # on init
    p_init = PositionalDict([("foo", "A"), ("foo", "B")])
    assert len(p_init) == 1
    assert p_init["foo"] == "B"

    # one by one
    p_setting = PositionalDict()
    p_setting["foo"] = "A"
    p_setting["foo"] = "B"
    assert len(p_setting) == 1
    assert p_setting["foo"] == "B"
