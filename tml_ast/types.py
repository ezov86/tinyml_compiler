from typing import List, Any

from .node import Node
from position import Position
from .visitor import Visitor


class Type(Node):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name


class SimpleType(Type):
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_simple_type(self)


class ParameterizedType(Type):
    def __init__(self, position: Position, name: str, types: List[Type]):
        super().__init__(position, name)
        self.types = types

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_parameterized_type(self)


class PolymorphType(Type):
    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_polymorph_type(self)


class FunType(Type):
    def __init__(self, position: Position, types: List[Type]):
        super().__init__(position, "fun")
        self.types = types
