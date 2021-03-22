from patterns.visitor import Visitor
from semantic.defs import Let, Typedef, TypeConstructor
from semantic.module import GlobalModule
from semantic.typing.types import SimpleType, ParameterizedType, PolymorphType


class HeaderGenerator(Visitor):
    def __init__(self):
        self.polymorph_types = []
        self.lets = []

    def visit(self, node, *args, **kwargs):
        dic = {'cls': node.__class__.__name__, **super().visit(node)}

        if hasattr(node, 'name') and node.name is not None:
            dic['name'] = node.name

        if hasattr(node, 'type'):
            dic['t'] = self.visit(node.type)

        return dic

    def visit_global_module(self, n: GlobalModule):
        self.lets = list(n.top_scope.lets.defs.values())

        dic = {
            'name': n.name,
            'lets': [self.visit(let) for let in n.top_scope.lets.defs.values()],
            'typedefs': [self.visit(typedef)for typedef in n.top_scope.typedefs.defs.values()],
            'pols': len(self.polymorph_types)
        }

        return dic

    def visit_type_constructor(self, n: TypeConstructor):
        return {}

    def visit_let(self, n: Let):
        return {}

    def visit_typedef(self, n: Typedef):
        return {'ctors': [self.lets.index(constructor) for constructor in n.constructors],
                'params': [self.visit(p) for p in n.params]}

    def visit_simple_type(self, n: SimpleType):
        return {}

    def visit_polymorph_type(self, n: PolymorphType):
        if n in self.polymorph_types:
            index = self.polymorph_types.index(n)
        else:
            index = len(self.polymorph_types)
            self.polymorph_types.append(n)

        return {'i': index}

    def visit_parameterized_type(self, n: ParameterizedType):
        return {'params': [self.visit(p) for p in n.params]}
