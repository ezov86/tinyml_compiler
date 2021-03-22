from position import Position
from .defs import Typedef, spec_name, InvalidParamTypeUsageException, ForeignLet
from .module import Module
from .typing.types import fun_type, t_int, t_float, t_bool, t_a, t_ref_a


class FunTypedef(Typedef):
    def __init__(self):
        super().__init__('fun', 0)

    def check_params_or_fail(self, params: list, position: Position):
        if len(params) < 1:
            raise InvalidParamTypeUsageException(self.name, position)


builtin_types = Module(spec_name('builtins.types'))

typedefs = {
    'float': Typedef('float'),
    'int': Typedef('int'),
    'string': Typedef('string'),
    'bool': Typedef('bool'),
    'ref': Typedef('ref', [t_a]),
    'unit':  Typedef('unit'),
    'fun': FunTypedef()
}

builtin_types.top_scope.typedefs.defs = typedefs
builtin_types.top_scope.lets.defs = {
    'True': ForeignLet('True').with_type(t_bool),
    'False': ForeignLet('False').with_type(t_bool)
}

t_int_int_int = fun_type([t_int, t_int], t_int)
t_float_float_float = fun_type([t_float, t_float], t_float)
t_int_int_bool = fun_type([t_int, t_int], t_bool)
t_float_float_bool = fun_type([t_float, t_float], t_bool)
t_a_a_bool = fun_type([t_a, t_a], t_bool)
t_bool_bool_bool = fun_type([t_bool, t_bool], t_bool)
t_if = fun_type([t_bool, t_a, t_a], t_a)

bin_ops_types = {
    # int -> int -> int
    '+': t_int_int_int,
    '-': t_int_int_int,
    '/': t_int_int_int,
    '*': t_int_int_int,
    '%': t_int_int_int,
    '>>': t_int_int_int,
    '<<': t_int_int_int,

    # float -> float -> float
    '+.': t_float_float_float,
    '-.': t_float_float_float,
    '/.': t_float_float_float,
    '*.': t_float_float_float,

    # int -> int -> bool
    '>': t_int_int_bool,
    '<': t_int_int_bool,
    '>=': t_int_int_bool,
    '<=': t_int_int_bool,

    # float -> float -> bool
    '>.': t_float_float_bool,
    '<.': t_float_float_bool,
    '>=.': t_float_float_bool,
    '<=.': t_float_float_bool,

    # `a -> `a -> bool
    '=': t_a_a_bool,
    '!=': t_a_a_bool,

    # bool -> bool -> bool
    '|': t_bool_bool_bool,
    '&': t_bool_bool_bool,
}

un_ops_types = {
    '-': fun_type([t_int], t_int),
    '~': fun_type([t_int], t_int),
    '!': fun_type([t_bool], t_bool),
    '$': fun_type([t_ref_a], t_a),
    'new': fun_type([t_a], t_ref_a)
}
