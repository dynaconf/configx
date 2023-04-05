from lib.core.tree import LeafNode, PathNode
from lib.shared.types import AllTypes, NodeType


def evaluate_node(node: NodeType) -> AllTypes | None:
    """
    Evaluates a node recursively into it's corresponding
    python data structure

    Args:
        node: PathNode or LeafNode object

    """
    return _evaluate_raw_types(node)


def _evaluate_raw_types(node: NodeType) -> AllTypes | None:
    """
    Recursive function for `evaluate_node`
    """
    if isinstance(node, LeafNode):
        return node.setting.raw_data
    elif isinstance(node, PathNode):
        data = None
        if node.type is dict:
            data = {}
            for child in node.children:
                data.update({child.name: _evaluate_raw_types(child)})
        elif node.type is list:
            data = []
            for child in node.children:
                data.append(_evaluate_raw_types(child))
        return data
