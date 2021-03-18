from typing import List

from .node import TypedNode
from .typing.types import PolymorphType


class BaseExpression(TypedNode):
    pass


class Group(BaseExpression, list):
    def __init__(self, body):
        BaseExpression().__init__()
        list(self).__init__(body)

    def get_type(self):
        if not self:
            return PolymorphType()
        else:
            return self[-1].type

    type = property(get_type)


class Var(BaseExpression):
    def __init__(self, let):
        super().__init__()
        self.let = let


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
    def __init__(self, expression, branches: List[MatchBranch]):
        super().__init__()
        self.expression = expression
        self.branches = branches


class LambdaFun(BaseExpression):
    def __init__(self, body: Group):
        super().__init__()
        self.args = []
        self.body = body


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
