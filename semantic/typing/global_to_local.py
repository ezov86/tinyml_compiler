from copy import copy

from patterns.visitor import Visitor
from .types import SimpleType, PolymorphType, ParameterizedType


class GlobalToLocalTypeVisitor(Visitor):
    """ Посетитель, заменяющий глобальные параметрические и полиморфные типы на локальные. """
    def __init__(self):
        # Словарь из глобальных типов (ключей) и локальных типов, на которые они были заменены (значения).
        self.already_replaced = {}
        # Локальные типы.
        self.local_types = []

    def visit(self, n, *args, **kwargs):
        if n in self.already_replaced:
            return self.already_replaced[n]
        elif n in self.local_types:
            return n
        else:
            local = super().visit(n)

            self.already_replaced[n] = local
            self.local_types.append(local)

            return local

    def visit_simple_type(self, n: SimpleType):
        return n

    def visit_polymorph_type(self, n: PolymorphType):
        return PolymorphType()

    def visit_parameterized_type(self, n: ParameterizedType):
        return ParameterizedType(n.name, [self.visit(p) for p in n.params])
