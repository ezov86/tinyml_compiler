from typing import List, Union, NewType, Any, Optional

Type = Union[NewType('SimpleType', Any), NewType('PolymorphType', Any), NewType('ParameterizedType', Any)]


class BaseType:
    def __init__(self, name: Optional[str]):
        self.name = name

    def is_compatible(self, t2: Type) -> bool:
        return False

    def replace_type(self, old_t: Type, new_t: Type):
        pass

    def __str__(self) -> str:
        return self.name


class SimpleType(BaseType):
    def is_compatible(self, t2: Type) -> bool:
        return is_polymorph_t(t2) or (is_simple_t(t2) and t2.name == self.name)


class PolymorphType(BaseType):
    def __init__(self):
        super().__init__(None)

    def is_compatible(self, t2: Type) -> bool:
        return True


class ParameterizedType(BaseType):
    def __init__(self, name: str, params: List[Type]):
        super().__init__(name)
        self.params = params

    def is_compatible(self, t2: Type) -> bool:
        if is_polymorph_t(t2):
            return True

        if (not is_param_t(t2)) or len(t2.params) != len(self.params) or t2.name != self.name:
            return False

        for p1, p2 in zip(self.params, t2.params):
            if not p1.is_compatible(p2):
                return False

        return True

    def replace_type(self, old_t: Type, new_t: Type):
        for p in self.params:
            p.replace_type(old_t, new_t)

        self.params = [new_t if p == old_t else p for p in self.params]

    def __str__(self) -> str:
        params_str = []

        for p in self.params:
            if is_fun_t(p) and is_fun_t(self):
                p_str = f'({str(p)})'
            else:
                p_str = str(p)

            params_str.append(str(p_str))

        if is_fun_t(self):
            if len(params_str) == 1:
                return f'-> {params_str[0]}'

            return ' -> '.join(params_str)

        return f'{self.name}<{", ".join(params_str)}>'


def is_simple_t(t: Type) -> bool:
    return isinstance(t, SimpleType)


def is_polymorph_t(t: Type) -> bool:
    return isinstance(t, PolymorphType)


def is_param_t(t: Type) -> bool:
    return isinstance(t, ParameterizedType)


def is_fun_t(t: Type) -> bool:
    return isinstance(t, ParameterizedType) and t.name == 'fun'


def fun_type(args: List[Type], ret: Optional[Type] = None) -> ParameterizedType:
    params = [*args]

    if ret is not None:
        params.append(ret)

    return ParameterizedType('fun', params)


t_unit = SimpleType('unit')
t_int = SimpleType('int')
t_float = SimpleType('float')
t_string = SimpleType('string')
t_bool = SimpleType('bool')
t_a = PolymorphType()
t_b = PolymorphType()
t_c = PolymorphType()
t_d = PolymorphType()
t_e = PolymorphType()
t_ref_a = ParameterizedType('ref', [t_a])
