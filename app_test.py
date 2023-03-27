"""
General sandbox file
"""

from dataclasses import dataclass
from typing import Any, reveal_type

import pytest

from lib.core.tree import Bucket as B
from lib.core.tree import Node as N
from lib.core.tree import Setting as S
from lib.core.tree import Tree as T
from lib.shared.utils import normalize_compound_type


def main():
    t = T()
    t.create_node("node", "this_is_a_string")
    t.create_node("foo", 1)
    t.create_node("compound", ["foo", "bar", {"level": 4}])
    t.show()


@pytest.mark.skip
def test_full_path():
    ...
    # a = N(S("foo", ""))
    # b = N("bar", a)
    # c = N("spam", b)
    # d = N("eggs", c)
    # assert d.full_path() == "/foo/bar/spam/eggs"


def test_setting():
    s = S("foo", 123)
    s = S("foo", "bar")


def test_create_node():
    t = T()
    t.create_node("node", "this_is_a_string")


def test_normalize_compound_type():
    # list should convert
    c = [1, "spam", {"foo": "bar"}]
    normalized = normalize_compound_type(c)
    assert normalized[0] == 1
    assert normalized[1] == "spam"
    assert normalized[2] == {"foo": "bar"}

    # dict should bypass
    d = {"name": "John", "age": 34, "items": [1, 2, 3, 4]}
    normalized_bypass = normalize_compound_type(d)
    assert normalized_bypass["name"] == "John"
    assert normalized_bypass["age"] == 34
    assert normalized_bypass["items"] == [1, 2, 3, 4]


if __name__ == "__main__":
    exit(main())
