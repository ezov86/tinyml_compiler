import tml_ast as ast
from semantic.expressions import Match
from semantic.module import Scope


class MatchBuilder:
    def __init__(self, ast_match: ast.Match, scope: Scope, visitor):
        self.ast_match = ast_match
        self.scope = scope
        self.visitor = visitor
        self.match = Match(visitor.visit(ast_match.expr, scope)).at(ast_match.position)
        self.patterns_are_type_variants = False
        self.ast_default_branch = None

    def process_patterns(self):
        for branch in self.ast_match.branches:
            pattern = branch.pattern

            if isinstance(pattern, ast.Var) \
                    and self.scope.lets.find(pattern.name) is None \
                    and self.ast_default_branch is None:
                self.ast_default_branch = branch

            if isinstance(pattern, ast.Apply) \
                    and isinstance(pattern.args[0], ast.Var) \
                    and self.scope.lets.find(pattern.args[0].name) is None:
                self.patterns_are_type_variants = True

    def visit_branches(self):
        for branch in self.ast_match.branches:
            if branch == self.ast_default_branch:
                self.match.default_branch = self.visitor.visit(branch, self.scope, self, is_default_branch=True)
                continue

            branch = self.visitor.visit(branch, self.scope, self)

            self.match.branches.append(branch)

    def check_exhaustivity(self):
        pass

    def result(self) -> Match:
        return self.match
