import unittest
from main import parse_source_code
from args import Args
from position import Position
from semantic.module import GlobalModule
from semantic.typing.polym_type_name_setter import PolymorphTypeNameSetter
from semantic.typing.types import fun_type, t_int, t_bool, t_string, t_float, t_a, t_b, t_c, t_d, ParameterizedType, \
    t_ref_a


class TestTypeInferer(unittest.TestCase):
    def setUp(self) -> None:
        Args().stop_after_type_inferring = True

    def test_simple(self):
        self.fun_counter = 1
        self.check('let f1 = fun(n) -> { if (n = 0) then 1 else n * f1(n - 1) }',
                   fun_type([t_int], t_int))
        self.check('let f2 = fun(a, b, c) -> { a = ""; b = 0; c = b }',
                   fun_type([t_string, t_int, t_int], t_bool))
        self.check('let f3 = fun(a, b, c) -> { let d = a = b; let e = c -. 0.2; a != c }',
                   fun_type([t_float, t_float, t_float], t_bool))

    def test_polymorph(self):
        self.fun_counter = 4
        self.check('let f4 = fun(f, x, y) -> { f(x) = y }',
                   fun_type([fun_type([t_a], t_b), t_a, t_b], t_bool))
        self.check('let f5 = fun(x, y, is_q) -> { '
                   '    let f = if (is_q) then '
                   '        fun(x) -> { x * x } '
                   '    else '
                   '        fun(x) -> { x }; '
                   '    f4(f, x, y)'
                   '}',
                   fun_type([t_int, t_int, t_bool], t_bool))
        self.check('let f6 = fun(f) -> { f4(f, "3", 3) }',
                   fun_type([fun_type([t_string], t_int)], t_bool))
        self.check('let f7 = fun(f, g, h, x, y) -> { f(g(h(x))) = y }',
                   fun_type([fun_type([t_a], t_b), fun_type([t_c], t_a), fun_type([t_d], t_c), t_d, t_b], t_bool))
        self.check('let f8 = fun(f, x) -> { f(f(f(x))) }',
                   fun_type([fun_type([t_a], t_a), t_a], t_a))

    def test_param(self):
        self.fun_counter = 9
        self.check('let f9 = fun(f, v, r) -> {'
                   '   let r2 = f(new v);'
                   '   (new r2) = $r'
                   '}',
                   fun_type(
                       [fun_type([t_ref_a], t_b), t_a, ParameterizedType('ref', [ParameterizedType('ref', [t_b])])],
                       t_bool))

    def check(self, code, expected_type):
        parse_source_code(f'module test {code}')

        actual = GlobalModule().top_scope.lets.find_or_fail(f'f{self.fun_counter}', Position.start()).type
        self.fun_counter += 1

        PolymorphTypeNameSetter().visit(expected_type)
        PolymorphTypeNameSetter().visit(actual)

        self.assertEqual(str(expected_type), str(actual))
