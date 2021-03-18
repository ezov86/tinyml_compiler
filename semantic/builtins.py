from position import Position
from .defs import TypeDef, spec_name, InvalidParamTypeUsageException
from .module import Module


class FunTypeDef(TypeDef):
    def __init__(self):
        super().__init__('fun', 0)

    def check_params_or_fail(self, params: list, position: Position):
        if len(params) < 1:
            raise InvalidParamTypeUsageException(self.name, position)


builtin_types = Module(spec_name('builtins.types'))

typedefs = {
    'float': TypeDef('float', 0),
    'int': TypeDef('int', 0),
    'bool': TypeDef('bool', 0),
    'ref': TypeDef('ref', 1),
    'unit':  TypeDef('unit', 0),
    'fun': FunTypeDef()
}

builtin_types.top_scope.typedefs.defs = typedefs
