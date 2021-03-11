from typing import List, Any

from .node import Node
from position import Position
from .visitor import Visitor


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

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_apply(self)


class Var(Expression):
    def __init__(self, position: Position, name: str):
        super().__init__(position)
        self.name = name

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_var(self)


class Const(Expression):
    def __init__(self, position: Position, _type, value: any):
        super().__init__(position)
        self.type = _type
        self.value = value

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_const(self)


class BinOperator(Expression):
    def __init__(self, position: Position, operation: str, left: Expression, right: Expression):
        super().__init__(position)
        self.operation = operation
        self.right = right
        self.left = left

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_bin_operator(self)


class UnaryOperator(Expression):
    def __init__(self, position: Position, operation, operand: Expression):
        super().__init__(position)
        self.operation = operation
        self.operand = operand

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_unary_operator(self)


class If(Expression):
    def __init__(self, position: Position, condition: Expression, then_branch: Expression, else_branch: Expression):
        super().__init__(position)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_if(self)


class MatchBranch(Node):
    def __init__(self, position: Position, pattern: Expression, body_expr: Expression):
        super().__init__(position)
        self.pattern = pattern
        self.body_expr = body_expr

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_match_branch(self)


class Match(Expression):
    def __init__(self, position: Position, expr: Expression, branches: List[MatchBranch]):
        super().__init__(position)
        self.expr = expr
        self.branches = branches

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_match(self)


class LambdaFun(Expression):
    def __init__(self, position: Position, args: List[str], body: Expression):
        super().__init__(position)
        self.args = args
        self.body = body

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_lambda_fun(self)


class ListCreate(Expression):
    def __init__(self, position: Position, values: Group):
        super().__init__(position)
        self.values = values

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_list_create(self)


class GetElementFromList(Expression):
    def __init__(self, position: Position, lst: Expression, index: Expression):
        super().__init__(position)
        self.list = lst
        self.index = index

    def accept(self, visitor: Visitor) -> Any:
        return visitor.visit_get_element_from_list(self)
