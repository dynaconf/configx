"""End-to-end testing of program flow"""
from __future__ import annotations

from core import (DictElement, ListElement, Node, ValueElement,
                  evaluate_component_tree, ingest_data, merge_tree,
                  reconcile_data, split_mixed_tree)


def test_ingest_merge_reconcile(data_a, expected, use_patch):
    # setup
    base_tree = Node(DictElement, "root")
    data = {}

    # ingest data
    tree_a = ingest_data(data_a)

    # merge-reconcile from scratch
    data_patches = merge_tree(base_tree, tree_a)
    reconcile_data(data, base_tree, data_patches, use_patch=use_patch)

    assert data == expected


def test_ingest_merge_reconcile_twice(data_a, data_b, expected, use_patch):
    # setup
    base_tree = Node(DictElement, "root")
    data = {}

    # ingest data
    tree_a = ingest_data(data_a)
    tree_b = ingest_data(data_b)

    # merge-reconcile from scratch
    data_patches = merge_tree(base_tree, tree_a)
    reconcile_data(data, base_tree, data_patches, use_patch=use_patch)

    # merge-reconcile from existing base_tree
    data_patches = merge_tree(base_tree, tree_b)
    reconcile_data(data, base_tree, data_patches, use_patch=use_patch)

    assert data == expected


def test_ingest_evaluate_merge_reconcile(data_a, expected, use_patch):
    # setup
    base_tree = Node(DictElement, "root")
    data = {}

    # ingest data
    tree_a = ingest_data(data_a)
    tree_b = ingest_data(data_b)  # contains Component NodeTypes

    # extract and evaluate components
    elements_tree, components_tree = split_mixed_tree(tree_a)

    # merge-reconcile from scratch
    data_patches_a = merge_tree(base_tree, elements_tree)
    reconcile_data(data, base_tree, data_patches_a)

    # re-integrate component_tree
    evaluated_tree = evaluate_component_tree(components_tree, context=data)
    data_patches_b = merge_tree(base_tree, evaluated_tree)
    reconcile_data(data, base_tree, data_patches_b)

    assert data == expected
