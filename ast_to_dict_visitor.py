from tml_ast import *
from patterns.visitor import Visitor


class AstToDictVisitor(Visitor):
    def visit_node(self, n: Node) -> dict:
        dic = n.__dict__
        new_dic = {'node_type': n.__class__.__name__}

        for child_name, child_value in dic.items():
            if child_name == 'position':
                child_name = 'line'
                child_value = dic['position'].line
            else:
                child_value = self.visit(child_value)

            new_dic[child_name] = child_value

        return new_dic

    def visit_group(self, n: Group):
        return self.visit_list(n)

    def visit_list(self, n: list) -> list:
        return [self.visit(el) for el in n]

    def visit_default(self, n, *args, **kwargs):
        if isinstance(n, Node):
            return self.visit_node(n)

        return n
