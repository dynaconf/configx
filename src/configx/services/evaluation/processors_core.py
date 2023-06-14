"""
Module responsible for keeping raw processors and related
functionality.
"""
from __future__ import annotations

from inspect import isfunction
from typing import Sequence

from configx.services.evaluation import builtin_processors
from configx.core.setting_tree import SettingTree
from configx.exceptions import TokenError
from configx.types import MISSING, ContextObject, RawProcessor, TreePath

_raw_processors: dict[str, RawProcessor] = {}


def add_processor(name: str, processor: RawProcessor):
    """Register RawProcessor"""
    _raw_processors[name] = processor


def get_processor(name: str):
    """Get registered processor to be used as a token."""
    name = name[1:] if name.startswith("@") else name
    try:
        return _raw_processors[name]
    except KeyError:
        raise TokenError(f"The token is not registered: {repr(name)}")


# initialize builtin processors


for name, processor in builtin_processors.__dict__.items():
    if isfunction(processor):
        processor_name = name.rpartition("_")[0]
        add_processor(processor_name, processor)

SUBSTITUTION_OPERATORS = [get_processor("jinja"), get_processor("format")]

# helpers


def build_context_from_tree(
    setting_tree: SettingTree, filter_by_paths: Sequence[TreePath] = MISSING
) -> ContextObject:
    ...


def build_context_from_dict(
    dict_data: dict, filter_by_paths: Sequence[TreePath] = MISSING
) -> ContextObject:
    ...
