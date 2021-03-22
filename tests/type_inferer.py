import unittest
from main import parse_source_code
from args import Args
from position import Position
from semantic.module import GlobalModule
from semantic.typing.polym_type_name_setter import PolymorphTypeNameSetter
from semantic.typing.types import fun_type, t_int, t_bool, t_string, t_float, t_a, t_b, t_c, t_d, ParameterizedType, \
    t_ref_a, SimpleType


class TestTypeInferer(unittest.TestCase):
    def setUp(self) -> None:
        Args().stop_after_type_inferring = True

    def test_simple(self):
        self.check('let f1 = fun(n) -> { if (n = 0) then 1 else n * f1(n - 1) }',
                   {'f1': fun_type([t_int], t_int)})
        self.check('let f2 = fun(a, b, c) -> { a = ""; b = 0; c = b }',
                   {'f2': fun_type([t_string, t_int, t_int], t_bool)})
        self.check('let f3 = fun(a, b, c) -> { let d = a = b; let e = c -. 0.2; a != c }',
                   {'f3': fun_type([t_float, t_float, t_float], t_bool)})

    def test_polymorph(self):
        self.check('let f4 = fun(f, x, y) -> { f(x) = y }',
                   {'f4': fun_type([fun_type([t_a], t_b), t_a, t_b], t_bool)})
        self.check('let f5 = fun(x, y, is_q) -> { '
                   '    let f = if (is_q) then '
                   '        fun(x) -> { x * x } '
                   '    else '
                   '        fun(x) -> { x }; '
                   '    f4(f, x, y)'
                   '}',
                   {'f5': fun_type([t_int, t_int, t_bool], t_bool)})
        self.check('let f6 = fun(f) -> { f4(f, "3", 3) }',
                   {'f6': fun_type([fun_type([t_string], t_int)], t_bool)})
        self.check('let f7 = fun(f, g, h, x, y) -> { f(g(h(x))) = y }',
                   {'f7': fun_type([fun_type([t_a], t_b), fun_type([t_c], t_a), fun_type([t_d], t_c), t_d, t_b],
                                   t_bool)})
        self.check('let f8 = fun(f, x) -> { f(f(f(x))) }',
                   {'f8': fun_type([fun_type([t_a], t_a), t_a], t_a)})
        self.check('let f14: `x -> `x -> `x = fun(a, b) -> { a = a } ',
                   {'f14': fun_type([t_bool, t_bool], t_bool)})

    def test_param(self):
        self.check('let f9 = fun(f, v, r) -> {'
                   '   let r2 = f(new v);'
                   '   (new r2) = $r'
                   '}',
                   {'f9': fun_type(
                       [fun_type([t_ref_a], t_b), t_a, ParameterizedType('ref', [ParameterizedType('ref', [t_b])])],
                       t_bool)})

    def test_type_constructors(self):
        self.check('type a = { f10, f11 = int * float * ref<ref<bool>>, f12 = bool }',
                   {
                       'f10': SimpleType('a'),
                       'f11': fun_type([t_int, t_float, ParameterizedType('ref', [ParameterizedType('ref', [t_bool])])],
                                       SimpleType('a')),
                       'f12': fun_type([t_bool], SimpleType('a'))
                   })
        self.check('type list<`a> = { Empty, Cons = `a * list<`a> }',
                   {
                       'Empty': ParameterizedType('list', [t_a]),
                       'Cons': fun_type([t_a, ParameterizedType('list', [t_a])], ParameterizedType('list', [t_a]))
                   })
        self.check('type b<`q> = { f13 = `q * b<b<`q>> }',
                   {'f13': fun_type([t_a, ParameterizedType('b', [ParameterizedType('b', [t_a])])],
                                    ParameterizedType('b', [t_a]))})

    def check(self, code, expected_types: dict):
        parse_source_code(f'module test {code}')

        for let_name, expected_type in expected_types.items():
            actual = GlobalModule().top_scope.lets.find_or_fail(let_name, Position.start()).type

            PolymorphTypeNameSetter().visit(expected_type)
            PolymorphTypeNameSetter().visit(actual)

            self.assertEqual(str(expected_type), str(actual))


if __name__ == '__main__':
    unittest.main()
