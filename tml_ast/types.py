from typing import List, Any

from .node import Node
from position import Position


class Type(Node):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name


class SimpleType(Type):
    pass


class ParameterizedType(Type):
    def __init__(self, position: Position, name: str, types: List[Type]):
        super().__init__(position, name)
        self.types = types


class PolymorphType(Type):
    pass


class FunType(Type):
    def __init__(self, position: Position, types: List[Type]):
        super().__init__(position, "fun")
        self.types = types
