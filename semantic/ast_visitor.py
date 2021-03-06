import json
from pathlib import Path

import tml_ast as ast
from errors import CompilationException, Error
from header_reader import HeaderReader
from patterns.visitor import Visitor
from position import Position
from .builtins import t_if, builtin_types, un_ops_types, bin_ops_types
from .defs import Let, FakeArg, Typedef, TypeConstructor
from .expressions import *
from .match_builder import MatchBuilder
from .module import GlobalModule, Scope, RedefinitionException
from .typing.ast_type_visitor import AstTypeVisitor
from .typing.inferer import GlobalTypeInferer, Constraint
from .typing.types import PolymorphType, fun_type, t_int


class InvalidUsageException(CompilationException):
    def __init__(self, name: str, position: Position):
        super().__init__(Error(f"неправильно количество аргументов у '{name}'", position))


class SemanticVisitor(Visitor):
    def visit_root(self, n: ast.Root) -> GlobalModule:
        GlobalModule().name = n.module_name
        GlobalModule().open_module(builtin_types)

        if n.imports is not None:
            self.visit(n.imports)

        if n.opens is not None:
            self.visit(n.opens)

        for definition in n.definitions:
            try:
                self.visit(definition, GlobalModule().top_scope)
            except CompilationException as e:
                e.handle()

        return GlobalModule()

    def visit_import(self, n: ast.Import):
        for module_path in n.modules:
            with open(Path(module_path).with_suffix('.tmlh'), 'r') as f:
                json_text = f.read()

            module = HeaderReader().read_module(json.loads(json_text))

            if n.do_open_namespace:
                GlobalModule().open_module(module)
            else:
                GlobalModule().import_module(module)

    def visit_let(self, n: ast.Let, scope: Scope):
        e = Let(n.name).at(n.position)
        scope.lets.add(e, e.position)

        if n.type_hint is not None:
            e.with_type(AstTypeVisitor(scope).visit(n.type_hint))

        e.lock_rec = True
        e.value = self.visit(n.expression, scope)
        e.lock_rec = False

        # e = (let a = x), t(a) = t(x)
        GlobalTypeInferer().add_constraint(Constraint(
            e.type_wrapper,
            e.value.type_wrapper,
            e
        ))

    def visit_literal(self, n: ast.Literal, scope: Scope) -> Literal:
        return Literal(n.value).with_type(AstTypeVisitor(scope).visit(n.type)).at(n.position)

    def visit_var(self, n: ast.Var, scope: Scope) -> Var:
        let = scope.lets.find_or_fail(n.name, n.position)

        return Var(let).at(n.position)

    def visit_apply(self, n: ast.Apply, scope: Scope):
        args = [self.visit(arg, scope) for arg in n.args]
        args_t = [arg.type for arg in args]

        e = Apply(self.visit(n.fun, scope), args).at(n.position)

        # t(f) = [t(a)] -> t(e).
        GlobalTypeInferer().add_constraint(Constraint(
            e.fun.type_wrapper,
            TypeWrapper(fun_type(args_t, e.type)),
            e,
            do_use_local_inferer=e.fun.is_const_fun(),
            args=args
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
            e,
            do_use_local_inferer=True
        ))

        return e

    def visit_unary_operator(self, n: ast.UnaryOperator, scope: Scope):
        operand = self.visit(n.operand, scope)

        e = UnaryOperator(n.operation, operand).at(n.position)

        # t(un_op(operation)) = t(a) -> t(e), a - операнд.
        GlobalTypeInferer().add_constraint(Constraint(
            TypeWrapper(un_ops_types[e.operation]),
            TypeWrapper(fun_type([e.operand.type], e.type)),
            e,
            do_use_local_inferer=True
        ))

        return e

    def visit_binary_operator(self, n: ast.BinaryOperator, scope: Scope):
        left = self.visit(n.left, scope)
        right = self.visit(n.right, scope)

        # TODO: здесь не учитываются операторы списков. Исправить это.
        e = BinaryOperator(n.operation, left, right).at(n.position)

        # t(bin_op(operation)) = t(a) -> t(b) -> t(e), a - левый операнд, b - правый.
        GlobalTypeInferer().add_constraint(Constraint(
            TypeWrapper(bin_ops_types[e.operation]),
            TypeWrapper(fun_type([left.type, right.type], e.type)),
            e,
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
        # TODO: здесь и в visit_get_element_from_list написан какой-то бред. Исправить это.
        n.values.reverse()
        create_list = Var(scope.lets.find_or_fail('list.Empty', n.position)).at(n.position)

        for element in n.values:
            # _TODO: тождество t(list_create) = t(l0) -> t(e) = ... = t(l(i-1)) -> t(e), где ln - элемент с индексом
            #  n, i - количество элементов в списке.
            create_list = Apply(Var(scope.lets.find_or_fail('::')).at(n.position),
                                [self.visit(element), create_list]).at(n.position)

        return create_list

    def visit_get_element_from_list(self, n: ast.GetElementFromList, scope: Scope):
        # _TODO: тождество t(get_element_from_list) = t(l) -> t(e).
        return GetElementFromList(self.visit(n.list, scope), self.visit(n.index, scope)).at(n.position)

    def visit_typedef(self, n: ast.Typedef, scope: Scope):
        params = {}
        for p in n.params:
            if p.name in params:
                raise RedefinitionException(p.name, n.position)

            params[p.name] = PolymorphType()

        typedef = Typedef(n.name, list(params.values())).at(n.position)
        scope.typedefs.add(typedef, n.position)

        for constructor in n.constructors:
            typedef.constructors.append(self.visit(constructor, scope, typedef, params))

        return typedef

    def visit_type_constructor(self, n: ast.TypeConstructor, scope: Scope, typedef: Typedef, params: dict):
        fields = []

        types_visitor = AstTypeVisitor(scope, len(params) != 0, params, True)

        if n.types is not None:
            for field in n.types:
                fields.append(types_visitor.visit(field))

        type_constructor = TypeConstructor(n.name, fields, typedef).at(n.position)
        scope.lets.add(type_constructor, n.position)

        return type_constructor

    def visit_match(self, n: ast.Match, scope: Scope):
        builder = MatchBuilder(n, scope, self)

        builder.process_patterns()
        builder.visit_branches()
        builder.check_exhaustivity()

        return builder.result().at(n.position)

    def visit_match_branch(self, n: ast.MatchBranch, scope: Scope, builder: MatchBuilder, is_default_branch=False):
        if is_default_branch:
            body_scope = ScopeWithParent(scope)
            pattern = Arg(n.pattern.name)
            body_scope.lets.add(pattern, n.pattern.position)

            body = self.visit(n.body, body_scope)
        elif builder.patterns_are_type_variants:
            if isinstance(n.pattern, ast.Var):
                constructor = scope.lets.find(n.pattern.name)
                body = self.visit(n.body, scope)
            else:
                constructor = scope.lets.find_or_fail(n.pattern.fun.name, n.pattern.position)

                if len(constructor.field_types) != len(n.pattern.args):
                    raise InvalidUsageException(constructor.name, n.pattern.position)

                body_scope = ScopeWithParent(scope)
                for field in n.pattern.args:
                    body_scope.lets.add(Arg(field.name), n.pattern.position)

                body = self.visit(n.body, body_scope)

            pattern = Literal(constructor.index).with_type(t_int).at(n.position)

            # t(c) = t(m_e)
            GlobalTypeInferer().add_constraint(Constraint(
                constructor.type_wrapper,
                builder.match.expression,
                pattern,
                do_use_local_inferer=True
            ))
        else:
            pattern = self.visit(n.pattern, scope)

            # t(p) = t(m_e)
            GlobalTypeInferer().add_constraint(Constraint(
                pattern.type_wrapper,
                builder.match.expression,
                pattern,
            ))

            body = self.visit(n.body, scope)

        # t(m) = t(b_e)
        GlobalTypeInferer().add_constraint(Constraint(
            body.type_wrapper,
            builder.match.type_wrapper,
            body
        ))

        return MatchBranch(pattern, body).at(n.position)
