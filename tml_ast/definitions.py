from typing import List, Optional

from position import Position
from .node import Node
from .types import Type, PolymorphType


class Definition(Node):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name


class Let(Definition):
    def __init__(self, position: Position, name: str, expression, type_hint: Optional[Type]):
        super().__init__(position, name)
        self.expression = expression
        self.type_hint = type_hint


class TypeConstructor(Definition):
    def __init__(self, position: Position, name: str, types: List[Type]):
        super().__init__(position, name)
        self.types = types


class Typedef(Definition):
    def __init__(self, position: Position, name: str, params: List[PolymorphType], constructors: List[TypeConstructor]):
        super().__init__(position, name)
        self.params = params
        self.constructors = constructors
