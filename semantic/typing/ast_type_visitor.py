from patterns.visitor import Visitor
import tml_ast as ast
from semantic.module import NotFoundException, Scope
from semantic.typing.types import PolymorphType, SimpleType, ParameterizedType


class AstTypeVisitor(Visitor):
    def __init__(self, scope: Scope, accept_pol_types=True, polymorph_params: dict = {},
                 fail_if_pol_type_not_found=False):
        self.scope = scope
        self.accept_pol_types = accept_pol_types
        self.polymorph_params = polymorph_params
        self.fail_if_pol_type_found = fail_if_pol_type_not_found

    def visit_polymorph_type(self, n: ast.PolymorphType):
        if not self.accept_pol_types:
            raise NotFoundException(n.name, n.position)

        if n.name in self.polymorph_params:
            return self.polymorph_params[n.name]

        if self.fail_if_pol_type_found:
            raise NotFoundException(n.name, n.position)

        t = PolymorphType()
        self.polymorph_params[n.name] = t

        return t

    def visit_simple_type(self, n: ast.SimpleType):
        self.scope.typedefs.find_or_fail(n.name, n.position).check_params_or_fail([], n.position)

        return SimpleType(n.name)

    def visit_parameterized_type(self, n: ast.ParameterizedType):
        self.scope.typedefs.find_or_fail(n.name, n.position).check_params_or_fail(n.params, n.position)

        type_params = [self.visit(t) for t in n.params]
        return ParameterizedType(n.name, type_params)
