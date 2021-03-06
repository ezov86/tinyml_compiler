from typing import List

from .node import Node
from position import Position


class Type(Node):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name


class SimpleType(Type):
    pass


class ParameterizedType(Type):
    def __init__(self, position: Position, name: str, params: list):
        super().__init__(position, name)
        self.params = params


class PolymorphType(Type):
    pass
