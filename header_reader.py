from typing import Union, List, Tuple

from semantic.defs import Typedef, ForeignLet, Let, TypeConstructor
from semantic.module import Module
from semantic.typing.types import SimpleType, PolymorphType, ParameterizedType


class HeaderReader:
    def __init__(self):
        self.polymorph_types = []
        self.lets = []
        self.typedefs = []
        # Таблица для связывания объявлений конструкторов и объявлений типов, которым они принадлежат.
        # В первом столбце находится индекс объявления типов в self.typedefs, а во втором - сам конструктор.
        self.constructor_to_typedef_binder_tab: List[Tuple[int, TypeConstructor]] = []

    def read_module(self, json_dic: dict) -> Module:
        module = Module(json_dic['name'])

        self.polymorph_types = [PolymorphType() for _ in range(json_dic['pols'])]

        for let in json_dic['lets']:
            let = self.read_let(let)

            module.top_scope.lets.add(let, None)
            self.lets.append(let)

        for typedef in json_dic['typedefs']:
            typedef = self.read_typedef(typedef)

            module.top_scope.typedefs.add(typedef, None)
            self.typedefs.append(typedef)

        # Связывание объявлений конструкторов с объявлениями типов.
        for typedef_index, constructor in self.constructor_to_typedef_binder_tab:
            constructor.typedef = self.typedefs[typedef_index]

        return module

    def read_let(self, json_dic: dict) -> Union[ForeignLet, TypeConstructor]:
        if json_dic['class'] == ForeignLet.__name__:
            return self.read_foreign_let(json_dic)
        else:
            return self.read_type_constructor(json_dic)

    def read_foreign_let(self, json_dic: dict) -> ForeignLet:
        return ForeignLet(json_dic['name']).with_type(self.read_type(json_dic['type']))

    def read_type_constructor(self, json_dic: dict) -> TypeConstructor:
        constructor = TypeConstructor(
            json_dic['name'],
            [self.read_type(field_type) for field_type in json_dic['fields']],
            typedef=None  # Это временное значение. После чтения всех объявлений типов произойдет связывание
            # конструкторов с объявлением типов
        ).with_type(self.read_type(json_dic['type']))

        self.constructor_to_typedef_binder_tab.append((json_dic['td_i'], constructor))

        return constructor

    def read_typedef(self, json_dic: dict) -> Typedef:
        typedef = Typedef(
            json_dic['name'],
            [self.read_type(p) for p in json_dic['params']]
        ).with_type(self.read_type(json_dic['type']))

        for constructor_index in json_dic['ctors']:
            typedef.constructors.append(self.lets[constructor_index])

        return typedef

    def read_type(self, json_dic: dict):
        if json_dic['class'] == SimpleType.__name__:
            return self.read_simple_type(json_dic)
        elif json_dic['class'] == PolymorphType.__name__:
            return self.read_polymorph_type(json_dic)
        else:
            return self.read_parameterized_type(json_dic)

    def read_simple_type(self, json_dic: dict) -> SimpleType:
        return SimpleType(json_dic['name'])

    def read_polymorph_type(self, json_dic: dict) -> PolymorphType:
        return self.polymorph_types[json_dic['i']]

    def read_parameterized_type(self, json_dic: dict) -> ParameterizedType:
        return ParameterizedType(json_dic['name'], [self.read_type(p) for p in json_dic['params']])
