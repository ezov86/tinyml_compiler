from typing import List, Optional

from .defs import Arg
from .module import ScopeWithParent
from .node import TypedNode
from .typing.inferer import TypeWrapper
from .typing.types import PolymorphType, fun_type


class BaseExpression(TypedNode):
    pass


class Group(BaseExpression, list):
    def __init__(self, body):
        BaseExpression.__init__(self)
        list.__init__(self, body)

    def is_const_fun(self) -> bool:
        if not self:
            return False
        else:
            return self[-1].is_const_fun()

    def get_type_wrapper(self):
        if not self:
            return TypeWrapper(PolymorphType())
        else:
            return self[-1].type_wrapper

    type_wrapper = property(get_type_wrapper)


class Var(BaseExpression):
    def __init__(self, let):
        super().__init__()
        self.let = let

    def is_const_fun(self) -> bool:
        return self.let.is_const_fun()

    def get_type_wrapper(self):
        return self.let.type_wrapper

    type_wrapper = property(get_type_wrapper)


class Apply(BaseExpression):
    def __init__(self, fun, args: list):
        super().__init__()
        self.fun = fun
        self.args = args


class BinaryOperator(BaseExpression):
    def __init__(self, operation: str, left_operand, right_operand):
        super().__init__()
        self.operation = operation
        self.left_operand = left_operand
        self.right_operand = right_operand


class UnaryOperator(BaseExpression):
    def __init__(self, operation: str, operand):
        super().__init__()
        self.operation = operation
        self.operand = operand


class If(BaseExpression):
    def __init__(self, condition, then_branch, else_branch):
        super().__init__()
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class MatchBranch(TypedNode):
    def __init__(self, pattern, body):
        super().__init__()
        self.pattern = pattern
        self.body = body


class Match(BaseExpression):
    def __init__(self, expression):
        super().__init__()
        self.expression = expression
        self.branches = []
        self.default_branch: Optional[MatchBranch] = None


class LambdaFun(BaseExpression, ScopeWithParent):
    def __init__(self, parent_scope):
        BaseExpression.__init__(self)
        ScopeWithParent.__init__(self, parent_scope)
        self.args = []
        self.body = Group([])

    def is_const_fun(self) -> bool:
        return True

    def add_arg(self, arg: Arg):
        self.lets.add(arg, arg.position)
        self.args.append(arg)

    def get_type_wrapper(self):
        return TypeWrapper(fun_type([arg.type for arg in self.args], self.body.type), True)

    type_wrapper = property(get_type_wrapper)


class ListCreate(BaseExpression):
    def __init__(self, values: list):
        super().__init__()
        self.values = values


class GetElementFromList(BaseExpression):
    def __init__(self, lst, index):
        super().__init__()
        self.list = lst
        self.index = index


class Literal(BaseExpression):
    def __init__(self, value):
        super().__init__()
        self.value = value


class CreateTuple(BaseExpression):
    def __init__(self, variant_index: int, values: list):
        super().__init__()
        self.variant_index = variant_index
        self.values = values


class GetValueFromTuple(BaseExpression):
    def __init__(self, _tuple, value_index: int):
        super().__init__()
        self.tuple = _tuple
        self.value_index = value_index
