from patterns.visitor import Visitor
from semantic.typing.types import PolymorphType, ParameterizedType, SimpleType


class PolymorphTypeNameSetter(Visitor):
    def __init__(self):
        self.already_visited = []
        # Счетчик полиморфных типов. Нужен для того, чтобы каждому полиморфному типу было дано уникальное имя.
        self.polymorph_types_counter = 0

    def visit_simple_type(self, n: SimpleType):
        pass

    def visit_polymorph_type(self, n: PolymorphType):
        if n in self.already_visited:
            return

        if self.polymorph_types_counter <= 25:
            n.name = f'`{chr(ord("a") + self.polymorph_types_counter)}'
        else:
            n.name = f'`t{self.polymorph_types_counter}'

        self.already_visited.append(n)

        self.polymorph_types_counter += 1

    def visit_parameterized_type(self, n: ParameterizedType):
        for p in n.params:
            self.visit(p)
