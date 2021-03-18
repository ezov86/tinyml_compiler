from errors import CompilationException, Error
from position import Position
from .node import TypedNode, Node


class InvalidParamTypeUsageException(CompilationException):
    def __init__(self, name: str, position: Position):
        super().__init__(Error(f'неправильное количество параметров для типа {name}', position))


class TypeDef(Node):
    def __init__(self, name: str, params_num: int):
        super().__init__()
        self.name = name
        self.params_num = params_num

    def check_params_or_fail(self, params: list, position: Position):
        """ Проверка правильности количества параметров для этого типа. Вынесено в отдельную функцию для того, чтобы в
         FunTypeDef (типе-функции) можно было указывать любое количество аргументов большее 1. """
        if len(params) != self.params_num:
            raise InvalidParamTypeUsageException(self.name, position)


class BaseLet(TypedNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class Let(BaseLet):
    def __init__(self, name: str, value):
        super().__init__(name)
        self.value = value


class Arg(BaseLet):
    pass


class FakeArg(Arg):
    def __init__(self):
        super().__init__('')


def spec_name(name: str) -> str:
    """ Создает специальное имя, состоящее из символов, которые невозможно включить в идентификатор в самом языке
    (чтобы гарантированно не происходил конфликт с объявленными переменными). """
    return f'#%${name}%$#'
