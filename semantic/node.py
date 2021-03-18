from position import Position
from .typing.types import TypeWrapper, Type, PolymorphType


class Node:
    def __init__(self):
        self.position = None


class TypedNode(Node):
    def __init__(self):
        super().__init__()
        self.type_wrapper = TypeWrapper(PolymorphType())

    def at(self, position: Position):
        self.position = position
        return self

    def with_type(self, t: Type):
        self.type_wrapper.type = t
        return self

    def get_type(self):
        return self.type_wrapper.type

    def set_type(self, t):
        self.type_wrapper.type = t

    type = property(get_type, set_type)
