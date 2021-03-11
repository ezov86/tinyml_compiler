class Visitor:
    def visit_apply(self, node): pass

    def visit_var(self, node): pass

    def visit_const(self, node): pass

    def visit_bin_operator(self, node): pass

    def visit_unary_operator(self, node): pass

    def visit_if(self, node): pass

    def visit_match_branch(self, node): pass

    def visit_match(self, node): pass

    def visit_lambda_fun(self, node): pass

    def visit_simple_type(self, node): pass

    def visit_parameterized_type(self, node): pass

    def visit_polymorph_type(self, node): pass

    def visit_list_create(self, node): pass

    def visit_get_element_from_list(self, node): pass
