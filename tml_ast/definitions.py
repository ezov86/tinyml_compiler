from typing import List

from .node import Node
from position import Position
from .expressions import Expression
from .types import Type, PolymorphType


class Definition(Node):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name


class Let(Definition):
    def __init__(self, position: Position, name: str, expression: Expression, type_hint: Type):
        super().__init__(position, name)
        self.expression = expression
        self.type_hint = type_hint


class TypeConstructor(Definition):
    def __init__(self, position: Position, name: str, types: List[Type]):
        super().__init__(position, name)
        self.types = types


class TypeDef(Definition):
    def __init__(self, position: Position, name: str, params: List[PolymorphType], constructors: List[TypeConstructor]):
        super().__init__(position, name)
        self.params = params
        self.constructors = constructors
