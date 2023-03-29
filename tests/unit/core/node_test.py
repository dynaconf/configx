"""
PathNode and LeafNode API behaviour and representation
"""

import pytest

from lib.core.tree import Node as N
from lib.core.tree import Setting as S


def test_BaseNode_mwe():
    """
    Should get full path of PathNode and LeafNodes
    """
