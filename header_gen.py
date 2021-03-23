from patterns.visitor import Visitor
from semantic.defs import Typedef, TypeConstructor, Let
from semantic.module import GlobalModule, Module
from semantic.typing.types import ParameterizedType, PolymorphType


class HeaderGenerator(Visitor):
    def __init__(self):
        self.polymorph_types = []
        self.lets = []
        self.typedefs = []

    def visit(self, node, *args, **kwargs):
        dic = super().visit(node)

        if not (isinstance(node, GlobalModule) or isinstance(node, Module)):
            if isinstance(node, Let):
                dic['class'] = 'ForeignLet'
            else:
                dic['class'] = node.__class__.__name__

        if hasattr(node, 'name') and node.name is not None:
            dic['name'] = node.name

        if hasattr(node, 'type'):
            dic['type'] = self.visit(node.type)

        return dic

    def visit_default(self, node, *args, **kwargs):
        return {}

    def visit_global_module(self, n: GlobalModule):
        self.lets = list(n.top_scope.lets.defs.values())
        self.typedefs = list(n.top_scope.typedefs.defs.values())

        dic = {
            'name': n.name,
            'lets': [self.visit(let) for let in self.lets],
            'typedefs': [self.visit(typedef) for typedef in self.typedefs],
            'pols': len(self.polymorph_types)
        }

        return dic

    def visit_type_constructor(self, n: TypeConstructor):
        return {
            'fields': [self.visit(field_type) for field_type in n.field_types],
            'td_i': self.typedefs.index(n.typedef)
        }

    def visit_module(self, n: Module):
        """ Отдельный метод для юнит-тестов (в реальных случая никто не должен передавать сюда обычный модуль). """
        # noinspection PyTypeChecker
        return self.visit_global_module(n)

    def visit_typedef(self, n: Typedef):
        return {
            'ctors': [self.lets.index(constructor) for constructor in n.constructors],
            'params': [self.visit(p) for p in n.params]
        }

    def visit_polymorph_type(self, n: PolymorphType):
        if n in self.polymorph_types:
            index = self.polymorph_types.index(n)
        else:
            index = len(self.polymorph_types)
            self.polymorph_types.append(n)

        return {'i': index}

    def visit_parameterized_type(self, n: ParameterizedType):
        return {
            'params': [self.visit(p) for p in n.params]
        }
