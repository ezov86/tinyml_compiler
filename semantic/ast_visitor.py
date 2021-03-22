from typing import Optional, Dict

import tml_ast as ast
from errors import CompilationException
from patterns.visitor import Visitor
from .builtins import t_if, builtin_types, un_ops_types, bin_ops_types
from .defs import Let, FakeArg
from .expressions import *
from .module import GlobalModule, Scope, NotFoundException
from .typing.inferer import GlobalTypeInferer, Constraint
from .typing.types import PolymorphType, SimpleType, ParameterizedType, fun_type


class SemanticVisitor(Visitor):
    def visit_root(self, n: ast.Root) -> GlobalModule:
        GlobalModule(n.module_name).opened_modules.append(builtin_types)

        for definition in n.definitions:
            self.visit(definition, GlobalModule().top_scope)

        return GlobalModule()

    def visit_let(self, n: ast.Let, scope: Scope):
        e = Let(n.name).at(n.position)
        scope.lets.add(e)

        if n.type_hint is not None:
            e.with_type(self.visit(n.type_hint, scope))

        e.lock_rec = True
        e.value = self.visit(n.expression, scope)
        e.lock_rec = False

        # e = (let a = x), t(a) = t(x)
        GlobalTypeInferer().add_constraint(Constraint(
            e.type_wrapper,
            e.value.type_wrapper,
            e.position
        ))

    def visit_literal(self, n: ast.Literal, scope: Scope) -> Literal:
        return Literal(n.value).with_type(self.visit(n.type, scope)).at(n.position)

    def visit_var(self, n: ast.Var, scope: Scope) -> Var:
        let = scope.lets.find_or_fail(n.name, n.position)

        return Var(let).at(n.position)

    def visit_polymorph_type(self, n: ast.PolymorphType, scope: Scope, params={}):
        if params:
            if n.name in params:
                return params[n.name]
        else:
            t = PolymorphType()
            params[n.name] = t
            return t

    def visit_simple_type(self, n: ast.SimpleType, scope: Scope, params={}):
        scope.typedefs.find_or_fail(n.name, n.position).check_params_or_fail([], n.position)

        return SimpleType(n.name)

    def visit_parameterized_type(self, n: ast.ParameterizedType, scope: Scope, params={}):
        scope.typedefs.find_or_fail(n.name, n.position).check_params_or_fail(n.params, n.position)

        type_params = [self.visit(t, scope, params) for t in n.params]
        return ParameterizedType(n.name, type_params)

    def visit_apply(self, n: ast.Apply, scope: Scope):
        args = [self.visit(arg, scope) for arg in n.args]
        args_t = [arg.type for arg in args]

        e = Apply(self.visit(n.fun, scope), args).at(n.position)

        # t(f) = [t(a)] -> t(e).
        GlobalTypeInferer().add_constraint(Constraint(
            e.fun.type_wrapper,
            TypeWrapper(fun_type(args_t, e.type)),
            e.position,
            do_use_local_inferer=e.fun.is_const_fun()
        ))

        return e

    def visit_if(self, n: ast.If, scope: Scope):
        condition = self.visit(n.condition, scope)
        then_branch = self.visit(n.then_branch, scope)
        else_branch = self.visit(n.else_branch, scope)

        e = If(condition, then_branch, else_branch).at(n.position)

        # t(if) = t(cond) -> t(then) -> t(else) -> t(e).
        GlobalTypeInferer().add_constraint(Constraint(
            TypeWrapper(t_if),
            TypeWrapper(fun_type([condition.type, then_branch.type, else_branch.type], e.type)),
            e.position,
            do_use_local_inferer=True
        ))

        return e

    def visit_unary_operator(self, n: ast.UnaryOperator, scope: Scope):
        operand = self.visit(n.operand, scope)

        # TODO: здесь и в visit_binary_operator не учитываются операторы списков. Исправить это.
        e = UnaryOperator(n.operation, operand).at(n.position)

        # t(un_op(operation)) = t(a) -> t(e), a - операнд.
        GlobalTypeInferer().add_constraint(Constraint(
            TypeWrapper(un_ops_types[e.operation]),
            TypeWrapper(fun_type([e.operand.type], e.type)),
            e.position,
            do_use_local_inferer=True
        ))

        return e

    def visit_binary_operator(self, n: ast.BinaryOperator, scope: Scope):
        left = self.visit(n.left, scope)
        right = self.visit(n.right, scope)

        e = BinaryOperator(n.operation, left, right).at(n.position)

        # t(bin_op(operation)) = t(a) -> t(b) -> t(e), a - левый операнд, b - правый.
        GlobalTypeInferer().add_constraint(Constraint(
            TypeWrapper(bin_ops_types[e.operation]),
            TypeWrapper(fun_type([left.type, right.type], e.type)),
            e.position,
            do_use_local_inferer=True
        ))

        return e

    def visit_group(self, n: ast.Group, scope: Scope):
        body = []

        for expr in n:
            try:
                expr = self.visit(expr, scope)
                if expr is not None:
                    body.append(expr)
            except CompilationException as e:
                e.handle()

        return Group(body).at(n.position)

    def visit_lambda_fun(self, n: ast.LambdaFun, scope: Scope):
        fun = LambdaFun(scope).at(n.position)

        for arg_name in n.args:
            try:
                fun.add_arg(Arg(arg_name))
            except CompilationException as e:
                e.handle()
                fun.args.append(FakeArg())

        fun.body = self.visit(n.body, fun)

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
