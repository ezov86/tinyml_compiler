from typing import List

from .node import Node
from position import Position


class Expression(Node):
    pass


class Group(Expression, list):
    def __init__(self, position: Position, expressions: List[Expression]):
        Expression.__init__(self, position)
        list.__init__(self, expressions)


class Apply(Expression):
    def __init__(self, position: Position, fun: Expression, args: List[Expression]):
        super().__init__(position)
        self.fun = fun
        self.args = args


class Var(Expression):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name


class Literal(Expression):
    def __init__(self, position: Position, _type, value: any):
        super().__init__(position)
        self.type = _type
        self.value = value


class BinaryOperator(Expression):
    def __init__(self, position: Position, operation: str, left: Expression, right: Expression):
        super().__init__(position)
        self.operation = operation
        self.right = right
        self.left = left


class UnaryOperator(Expression):
    def __init__(self, position: Position, operation, operand: Expression):
        super().__init__(position)
        self.operation = operation
        self.operand = operand


class If(Expression):
    def __init__(self, position: Position, condition: Expression, then_branch: Expression, else_branch: Expression):
        super().__init__(position)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch


class MatchBranch(Node):
    def __init__(self, position: Position, pattern: Expression, body_expr: Expression):
        super().__init__(position)
        self.pattern = pattern
        self.body_expr = body_expr


class Match(Expression):
    def __init__(self, position: Position, expr: Expression, branches: List[MatchBranch]):
        super().__init__(position)
        self.expr = expr
        self.branches = branches


class LambdaFun(Expression):
    def __init__(self, position: Position, args: List[str], body: Expression):
        super().__init__(position)
        self.args = args
        self.body = body


class ListCreate(Expression):
    def __init__(self, position: Position, values: Group):
        super().__init__(position)
        self.values = values


class GetElementFromList(Expression):
    def __init__(self, position: Position, lst: Expression, index: Expression):
        super().__init__(position)
        self.list = lst
        self.index = index
