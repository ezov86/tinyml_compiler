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
    def __init__(self, position: Position, name: str, params: List[Type]):
        super().__init__(position, name)
        self.params = params


class PolymorphType(Type):
    pass


class FunType(Type):
    def __init__(self, position: Position, types: List[Type]):
        super().__init__(position, "fun")
        self.types = types
