from errors import CompilationException, Error
from position import Position
from .node import TypedNode
from .typing.inferer import TypeWrapper
from .typing.types import SimpleType, ParameterizedType, fun_type


class InvalidParamTypeUsageException(CompilationException):
    def __init__(self, name: str, position: Position):
        super().__init__(Error(f'неправильное количество параметров для типа {name}', position))


class TypeConstructor(TypedNode):
    def __init__(self, name: str, field_types: list, typedef):
        super().__init__()
        self.name = name
        self.field_types = field_types
        self.typedef = typedef

    def get_type_wrapper(self):
        if not self.field_types:
            t = self.typedef.type
        else:
            t = fun_type(self.field_types, self.typedef.type)

        return TypeWrapper(t)

    def is_const_fun(self) -> bool:
        return True

    def get_index(self):
        return self.typedef.constructors.index(self)

    type_wrapper = property(get_type_wrapper)
    index = property(get_index)


class Typedef(TypedNode):
    def __init__(self, name: str, params: list = []):
        super().__init__()
        self.name = name
        self.params = params
        self.constructors = []

    def check_params_or_fail(self, params: list, position: Position):
        """ Проверка правильности количества параметров для этого типа. Вынесено в отдельную функцию для того, чтобы в
         FunTypedef (типе-функции) можно было указывать любое количество аргументов большее 1. """
        if len(params) != len(self.params):
            raise InvalidParamTypeUsageException(self.name, position)

    def get_type_wrapper(self):
        if not self.params:
            return TypeWrapper(SimpleType(self.name))
        else:
            return TypeWrapper(ParameterizedType(self.name, self.params))

    type_wrapper = property(get_type_wrapper)


class BaseLet(TypedNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class Let(BaseLet):
    def __init__(self, name: str):
        super().__init__(name)
        self.value = None
        self.lock_rec = False

    def is_const_fun(self) -> bool:
        if self.lock_rec:
            return True

        return self.value.is_const_fun()


class ForeignLet(BaseLet):
    def is_const_fun(self) -> bool:
        return True


class Arg(BaseLet):
    pass


class FakeArg(Arg):
    def __init__(self):
        super().__init__('')


def spec_name(name: str) -> str:
    """ Создает специальное имя, состоящее из символов, которые невозможно включить в идентификатор в самом языке
    (чтобы гарантированно не происходил конфликт с объявленными переменными). """
    return f'#%${name}%$#'
