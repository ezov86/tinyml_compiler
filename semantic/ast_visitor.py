from typing import Optional, Dict

import tml_ast as ast
from errors import CompilationException, Error
from patterns.visitor import Visitor
from position import Position
from .defs import Let, FakeArg
from .expressions import *
from .module import Module, GlobalModule, Scope, NotFoundException
from .typing.types import PolymorphType, SimpleType, ParameterizedType


class SemanticVisitor(Visitor):
    def visit_root(self, n: ast.Root, builtin_modules: List[Module]) -> GlobalModule:
        GlobalModule().init(n.module_name)
        GlobalModule().opened_modules = builtin_modules

        for definition in n.definitions:
            self.visit(definition, GlobalModule().top_scope)

        return GlobalModule()

    def visit_let(self, n: ast.Let, scope: Scope):
        let = Let(n.name, self.visit(n.expression, scope)).at(n.position)

        if n.type_hint is not None:
            let.with_type(self.visit(n.type_hint, GlobalModule().top_scope))

        scope.lets.add(let)

    def visit_literal(self, n: ast.Literal, scope: Scope) -> Literal:
        return Literal(n.value).with_type(self.visit(n.type, scope)).at(n.position)

    def visit_var(self, n: ast.Var, scope: Scope) -> Optional[Var]:
        let = scope.lets.find(n.name)
        if let is None:
            NotFoundException(n.name, n.position)
            return

        return Var(let).at(n.position)

    def visit_polymorph_type(self, n: ast.PolymorphType, scope: Scope, params: Optional[Dict[str, PolymorphType]] = []):
        if params:
            if n.name in params:
                return params[n.name]

            raise NotFoundException(n.name, n.position)

        return PolymorphType()

    def visit_simple_type(self, n: ast.SimpleType, scope: Scope, params: Optional[Dict[str, PolymorphType]] = []):
        scope.typedefs.find_or_fail(n.name, n.position).check_params_or_fail([], n.position)

        return SimpleType(n.name)

    def visit_parameterized_type(self, n: ast.ParameterizedType, scope: Scope,
                                 params: Optional[Dict[str, PolymorphType]] = []):
        scope.typedefs.find_or_fail(n.name, n.position).check_params_or_fail(n.params)

        type_params = [self.visit(t, scope, params) for t in n.params]
        return ParameterizedType(n.name, type_params)

    def visit_apply(self, n: ast.Apply, scope: Scope):
        args = [self.visit(arg, scope) for arg in n.args]

        # TODO: тождество t(f) = [t(a)] -> t(e).

        return Apply(self.visit(n.fun, scope), args).at(n.position)

    def visit_if(self, n: ast.If, scope: Scope):
        condition = self.visit(n.condition)
        then_branch = self.visit(n.then_branch, scope)
        else_branch = self.visit(n.else_branch, scope)

        # TODO: тождество t(if) = t(cond) -> t(then) -> t(else) -> t(e).

        return If(condition, then_branch, else_branch).at(n.position)

    def visit_unary_operator(self, n: ast.UnaryOperator, scope: Scope):
        operand = self.visit(n.operand, scope)

        # TODO: тождество t(un_op(operation)) = t(a) -> t(e), где a - операнд.

        return UnaryOperator(n.operation, operand).at(n.position)

    def visit_binary_operator(self, n: ast.BinaryOperator, scope: Scope):
        left = self.visit(n.left, scope)
        right = self.visit(n.right, scope)

        # TODO: тождество t(bin_op(operation)) = t(a) -> t(b) -> t(e), где a - левый операнд, а b - правый.

        return BinaryOperator(n.operation, left, right).at(n.position)

    def visit_group(self, n: ast.Group, scope: Scope):
        body = []

        for expr in n:
            try:
                body.append(self.visit(expr, scope))
            except CompilationException as e:
                e.handle()

        return Group(body).at(n.position)

    def visit_lambda_fun(self, n: ast.LambdaFun):
        fun = LambdaFun(self.visit(n.body)).at(n.position)

        for arg in n.args:
            try:
                fun.args.append(self.visit(arg))
            except CompilationException as e:
                e.handle()
                fun.args.append(FakeArg())

        return fun

    def visit_list_create(self, n: ast.ListCreate, scope: Scope):
        n.values.reverse()
        create_list = Var(scope.lets.find_or_fail('list.Empty', n.position)).at(n.position)

        for element in n.values:
            # TODO: тождество t(list_create) = t(l0) -> t(e) = ... = t(l(i-1)) -> t(e), где ln - элемент с индексом
            #  n, i - количество элементов в списке.
            create_list = Apply(Var(scope.lets.find_or_fail('::')).at(n.position),
                                [self.visit(element), create_list]).at(n.position)

        return create_list

    def visit_get_element_from_list(self, n: ast.GetElementFromList, scope: Scope):
        # TODO: тождество t(get_element_from_list) = t(l) -> t(e).
        return GetElementFromList(self.visit(n.list, scope), self.visit(n.index, scope)).at(n.position)
