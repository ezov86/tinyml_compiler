from typing import List, Union, NewType, Any, Optional

Type = Union[NewType('SimpleType', Any), NewType('PolymorphType', Any), NewType('ParameterizedType', Any)]


class BaseType:
    def is_compatible(self, t2: Type) -> bool:
        return False

    def set_name(self, polymorph_types_counter: int) -> int:
        return polymorph_types_counter

    def replace(self, old_t: Type, new_t: Type):
        pass


class SimpleType(BaseType):
    def __init__(self, name: str):
        self.name = name

    def is_compatible(self, t2: Type) -> bool:
        return is_polymorph_t(t2) or (is_simple_t(t2) and t2.name == self.name)

    def set_name(self, polymorph_types_counter: int) -> int:
        return polymorph_types_counter


class PolymorphType(BaseType):
    def __init__(self):
        self.name = None

    def set_name(self, polymorph_types_counter: int) -> int:
        if self.name is None:
            return polymorph_types_counter

        if polymorph_types_counter <= 25:
            self.name = f'`{chr(ord("a") + 25)}'

        self.name = f'`t{polymorph_types_counter}'

        return polymorph_types_counter + 1


class ParameterizedType(BaseType):
    def __init__(self, name: str, params: List[Type]):
        self.name = name
        self.params = params

    def is_compatible(self, t2: Type) -> bool:
        if (not is_polymorph_t(t2)) or not is_param_t(t2):
            return False

        if len(t2.params) != len(self.params) or t2.name != self.name:
            return False

        for p1, p2 in zip(self.params, t2.params):
            if not p1.is_compatible(p2):
                return False

        return True

    def set_name(self, polymorph_types_counter: int) -> int:
        for p in self.params:
            polymorph_types_counter = p.set_name(polymorph_types_counter)

        return polymorph_types_counter

    def replace(self, old_t: Type, new_t: Type):
        for p in self.params:
            p.replace(old_t, new_t)

        self.params = [new_t if p == old_t else p for p in self.params]


class TypeWrapper:
    """ Обертка для типов. Нужна из-за того, что во время типа типы меняют свои типы (классы), например с PolymorphType
    на SimpleType. """
    def __init__(self, t: Type):
        self.type = t


def is_simple_t(t: Type) -> bool:
    return isinstance(t, SimpleType)


def is_polymorph_t(t: Type) -> bool:
    return isinstance(t, PolymorphType)


def is_param_t(t: Type) -> bool:
    return isinstance(t, ParameterizedType)


def is_fun_t(t: Type) -> bool:
    return isinstance(t, ParameterizedType) and t.name == 'fun'


def fun_type(args: List[Type], ret: Optional[Type] = None):
    if ret is None:
        args += [ret]

    return ParameterizedType('fun', args)
