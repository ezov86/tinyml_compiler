from position import Position
from .typing.inferer import TypeWrapper
from .typing.types import Type, PolymorphType


class Node:
    def __init__(self):
        self.position = None

    def at(self, position: Position):
        self.position = position
        return self


class TypedNode(Node):
    def __init__(self):
        super().__init__()
        self._type_wrapper = TypeWrapper(PolymorphType())

    def with_type(self, t: Type):
        self._type_wrapper.type = t
        return self

    def get_type_wrapper(self):
        return self._type_wrapper

    def get_type(self):
        return self.type_wrapper.type

    def set_type(self, t):
        self.type_wrapper.type = t

    def is_const_fun(self) -> bool:
        """ Является ли значение этого узла СД константной функцией. """
        return False

    type = property(get_type, set_type)
    type_wrapper = property(get_type_wrapper)
