from ply import yacc

from errors import CompilationException, Error
from tml_ast import *

# Без этого импорта не будет работать ply.yacc
# noinspection PyUnresolvedReferences
from .lexer import tokens


class InvalidSyntaxException(CompilationException):
    def __init__(self, p):
        super().__init__(Error(f"синтаксическая ошибка в '{p.value}'", Position.from_parser_token(p)))


class UnexpectedEofException(CompilationException):
    def __init__(self):
        super().__init__(Error('неожиданный конец файла'))


precedence = (
    ('left', 'PUT'),
    ('left', 'NEW'),
    ('left', 'THEN', 'ELSE'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ', 'BIGGER', 'LESS', 'BEQ', 'LEQ', 'BIGGER_FLOAT', 'LESS_FLOAT', 'BEQ_FLOAT', 'LEQ_FLOAT'),
    ('left', 'CONS', 'CONCAT'),
    ('left', 'RSHIFT', 'LSHIFT'),
    ('left', 'BOR', 'BAND'),
    ('left', 'PLUS', 'MINUS', 'FLOAT_PLUS', 'FLOAT_MINUS'),
    ('left', 'MUL', 'DIV', 'MOD', 'FLOAT_MUL', 'FLOAT_DIV'),
    ('right', 'UMINUS', 'NOT', 'GETVAL', 'BNOT')
)


def list_rule(p, el_i=1, list_i=3, el_len=1):
    """
    Вспомогательная функция для разбора списков.

    :param p: массив терминалов и нетерминалов.
    :param el_i: индекс элемента.
    :param list_i: индекс вложенного списка.
    :param el_len: количество терминалов и нетерминалов для режима работы с единственным элементом.
    :return:
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == el_len + 1:
        p[0] = [p[el_i]]
    else:
        p[0] = [p[el_i]] + p[list_i]

    return p[0]


def _pass(p, i=1):
    p[0] = p[i]


def pass_or_empty(p):
    if len(p) == 0:
        p[0] = None
    else:
        p[0] = p[1]


def p_root(p):
    """ root : MODULE ID import_or_none open_or_none defs_or_none """
    p[0] = Root(p[2], p[3], p[4], p[5])


def p_import_or_none(p):
    """ import_or_none  : _empty
                        | import """
    _pass(p)


def p_open_or_none(p):
    """ open_or_none    : _empty
                        | open """
    _pass(p)


def p_defs_or_none(p):
    """ defs_or_none    : defs
                        | _empty_list """
    _pass(p)


def p_defs(p):
    """ defs    : def
                | def defs """
    list_rule(p, list_i=2)


def p_def(p):
    """ def : let
            | type_def """
    _pass(p)


def p_let(p):
    """ let : LET ID type_hint_or_none EQ expr """
    p[0] = Let(Position.from_parser_ctx(p), p[2], p[5], p[3])


def p_type_hint_or_none(p):
    """ type_hint_or_none   : type_hint
                            | _empty """
    _pass(p)


def p_type_hint(p):
    """ type_hint : COLON type """
    _pass(p, 2)


def p_type_def(p):
    """ type_def : TYPE ID polymorph_type_params_or_none EQ LBRACE type_constructors RBRACE"""
    p[0] = Typedef(Position.from_parser_ctx(p), p[2], p[3], p[6])


def p_polymorph_type_params_or_none(p):
    """ polymorph_type_params_or_none   : polymorph_type_params
                                        | _empty_list """
    _pass(p)


def p_polymorph_type_params(p):
    """ polymorph_type_params : LANGLE polymorph_types_list RANGLE """
    _pass(p, 2)


def p_polymorph_types_list(p):
    """ polymorph_types_list    : polymorph_type
                                | polymorph_type COMMA polymorph_type """
    list_rule(p)


def p_type_constructors(p):
    """ type_constructors   : type_constructor
                            | type_constructor COMMA type_constructors """
    list_rule(p)


def p_type_constructor(p):
    """ type_constructor : ID types_product_or_none """
    p[0] = TypeConstructor(Position.from_parser_ctx(p), p[1], p[2])


def p_types_product_or_none(p):
    """ types_product_or_none   : _empty
                                | types_product_with_eq """
    _pass(p)


def p_types_product_with_eq(p):
    """ types_product_with_eq   : EQ types_product """
    _pass(p, 2)


def p_types_product(p):
    """ types_product   : type
                        | type MUL types_product """
    list_rule(p)


def p_open(p):
    """ open : OPEN modules_list """
    p[0] = Import(Position.from_parser_ctx(p), p[2], True)


def p_import(p):
    """ import : IMPORT modules_list """
    p[0] = Import(Position.from_parser_ctx(p), p[2])


def p_modules_list(p):
    """ modules_list    : str
                        | str COMMA modules_list """
    list_rule(p)


def p_type(p):
    """ type    : atomic_type
                | fun_type """
    _pass(p)


def p_atomic_type(p):
    """ atomic_type : simple_type
                    | param_type
                    | polymorph_type
                    | type_in_par """
    _pass(p)


def p_simple_type(p):
    """ simple_type : ID """
    p[0] = SimpleType(Position.from_parser_ctx(p), p[1])


def p_param_type(p):
    """ param_type : ID LANGLE types_list RANGLE """
    p[0] = ParameterizedType(Position.from_parser_ctx(p), p[1], p[3])


def p_types_list(p):
    """ types_list  : type
                    | type COMMA types_list """
    list_rule(p)


def p_fun_type(p):
    """ fun_type    : fun_type_arg
                    | fun_type_args """
    p[0] = ParameterizedType(Position.from_parser_ctx(p), 'fun', p[1])


def p_fun_type_arg(p):
    """ fun_type_arg : ARROW single_type_to_list """
    p[0] = p[2]


def p_single_type_to_list(p):
    """ single_type_to_list : atomic_type """
    p[0] = [p[1]]


def p_fun_type_args(p):
    """ fun_type_args : atomic_type ARROW right_arg_type """
    p[0] = [p[1]] + p[3]


def p_right_arg_type(p):
    """ right_arg_type  : fun_type_args
                        | single_type_to_list """
    _pass(p)


def p_polymorph_type(p):
    """ polymorph_type : POLYMORPH_TYPE """
    p[0] = PolymorphType(Position.from_parser_ctx(p), p[1])


def p_type_in_par(p):
    """ type_in_par : LPAR type RPAR """
    _pass(p, 2)


def p_expr(p):
    """ expr    : const
                | var
                | if
                | group
                | apply
                | match
                | fun
                | bin_op
                | un_op
                | list
                | get_el """
    _pass(p)


def p_binop(p):
    """ bin_op  : expr PUT expr
                | expr EQ expr
                | expr LANGLE expr %prec LESS
                | expr RANGLE expr %prec BIGGER
                | expr LESS_FLOAT expr
                | expr BIGGER_FLOAT expr
                | expr NEQ expr
                | expr BEQ expr
                | expr LEQ expr
                | expr BEQ_FLOAT expr
                | expr LEQ_FLOAT expr
                | expr FLOAT_PLUS expr
                | expr FLOAT_MINUS expr
                | expr FLOAT_MUL expr
                | expr FLOAT_DIV expr
                | expr PLUS expr
                | expr MINUS expr
                | expr MUL expr
                | expr DIV expr
                | expr MOD expr
                | expr CONS expr
                | expr CONCAT expr
                | expr OR expr
                | expr AND expr
                | expr BOR expr
                | expr BAND expr
                | expr LSHIFT expr
                | expr RSHIFT expr """
    p[0] = BinaryOperator(Position.from_parser_ctx(p), p[2], p[1], p[3])


def p_un_op(p):
    """ un_op   : NOT expr
                | MINUS expr %prec UMINUS
                | FLOAT_MINUS expr %prec UMINUS
                | BNOT expr
                | NEW expr
                | GETVAL expr"""
    p[0] = UnaryOperator(Position.from_parser_ctx(p), p[1], p[2])


def p_list(p):
    """ list : LBRACK expr_comma_list_or_none RBRACK """
    pos = Position.from_parser_ctx(p)
    p[0] = ListCreate(pos, Group(pos, p[2]))


def p_get_el(p):
    """ get_el : list_expr LBRACK expr RBRACK """
    p[0] = GetElementFromList(Position.from_parser_ctx(p), p[1], p[3])


def p_list_expr(p):
    """ list_expr   : group
                    | apply
                    | get_el
                    | var
                    | list """
    _pass(p)


def p_group(p):
    """ group : LPAR expr RPAR """
    _pass(p, 2)


def p_var(p):
    """ var : ID """
    p[0] = Var(Position.from_parser_ctx(p), p[1])


def p_if(p):
    """ if : IF group THEN expr ELSE expr """
    p[0] = If(Position.from_parser_ctx(p), p[2], p[4], p[6])


def p_apply(p):
    """ apply : apply_fun_expr LPAR expr_comma_list_or_none RPAR"""
    p[0] = Apply(Position.from_parser_ctx(p), p[1], p[3])


def p_match(p):
    """ match : MATCH expr LBRACE match_branches RBRACE """
    p[0] = Match(Position.from_parser_ctx(p), p[2], p[4])


def p_match_branches(p):
    """ match_branches  : match_branch
                        | match_branch COMMA match_branches """
    list_rule(p)


def p_match_branch(p):
    """ match_branch : expr ARROW match_branch_body """
    pos = Position.from_parser_ctx(p)
    p[0] = MatchBranch(pos, p[1], Group(pos, [p[3]]))


def p_match_branch_body(p):
    """ match_branch_body   : expr
                            | match_branch_body_expr_group """
    _pass(p)


def p_match_branch_body_expr_group(p):
    """ match_branch_body_expr_group : LBRACE expr_semicolon_list RBRACE """
    _pass(p, 2)


def p_expr_semicolon_list(p):
    """ expr_semicolon_list : expr
                            | expr SEMICOLON expr_semicolon_list """
    list_rule(p)


def p_apply_fun_expr(p):
    """ apply_fun_expr  : group
                        | apply
                        | var """
    _pass(p)


def p_expr_comma_list_or_none(p):
    """ expr_comma_list_or_none  : expr_comma_list
                                | _empty_list """
    _pass(p)


def p_expr_comma_list(p):
    """ expr_comma_list  : expr
                        | expr COMMA expr_comma_list """
    list_rule(p)


def p_fun(p):
    """ fun : FUN LPAR args_list_or_none RPAR ARROW LBRACE fun_body RBRACE """
    pos = Position.from_parser_ctx(p)
    p[0] = LambdaFun(pos, p[3], Group(pos, p[7]))


def p_args_list_or_none(p):
    """ args_list_or_none   : args_list
                            | _empty_list """
    _pass(p)


def p_args_list(p):
    """ args_list   : ID
                    | ID COMMA args_list """
    list_rule(p)


def p_fun_body(p):
    """ fun_body    : fun_body_stmt
                    | fun_body_stmt SEMICOLON fun_body """
    list_rule(p)


def p_fun_body_stmt(p):
    """ fun_body_stmt   : expr
                        | let """
    _pass(p)


def p__empty(p):
    """ _empty : """
    p[0] = None


def p__empty_list(p):
    """ _empty_list : """
    p[0] = []


def p_const(p):
    """ const   : str_const
                | int_const
                | float_const
                | unit """
    _pass(p)


def p_str_const(p):
    """ str_const : str """
    pos = Position.from_parser_ctx(p)
    p[0] = Literal(pos, SimpleType(pos, 'string'), p[1])


def p_int_const(p):
    """ int_const : INT """
    pos = Position.from_parser_ctx(p)
    p[0] = Literal(pos, SimpleType(pos, 'int'), int(p[1]))


def p_float_const(p):
    """ float_const : FLOAT """
    pos = Position.from_parser_ctx(p)
    p[0] = Literal(pos, SimpleType(pos, 'float'), float(p[1]))


def p_unit(p):
    """ unit : LPAR RPAR """
    pos = Position.from_parser_ctx(p)
    p[0] = Literal(pos, SimpleType(pos, 'unit'), None)


def p_str(p):
    """ str : STR """
    p[0] = p[1][1:-1]


def p_error(p):
    if p is None:
        UnexpectedEofException().handle()
    else:
        InvalidSyntaxException(p).handle()


parser = yacc.yacc()
