from tml_ast.expressions import Group
from tml_ast.node import Node
from visitor import Visitor


class AstToDictVisitor(Visitor):
    def visit_node(self, node: Node) -> dict:
        dic = node.__dict__
        new_dic = {'node_type': node.__class__.__name__}

        for child_name, child_value in dic.items():
            if child_name == 'position':
                child_name = 'line'
                child_value = dic['position'].line
            else:
                child_value = self.visit(child_value)

            new_dic[child_name] = child_value

        return new_dic

    def visit_group(self, node: Group):
        return self.visit_list(node)

    def visit_list(self, node: list) -> list:
        return [self.visit(el) for el in node]

    def visit_default(self, node, *args, **kwargs):
        if isinstance(node, Node):
            return self.visit_node(node)

        return node
