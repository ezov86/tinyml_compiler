from typing import Any

from position import Position


class Node:
    def __init__(self, position: Position):
        self.position = position


def to_json(x):
    dic = x.__dict__
    if 'position' in dic:
        dic['line'] = x.position.line
        dic['node_type'] = x.__class__.__name__
        del dic['position']

    return dic
