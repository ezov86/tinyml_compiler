import unittest
from typing import Dict

from args import Args
from main import parse_source_code
from semantic.typing.types import fun_type, t_int, t_bool, t_string, t_float, t_a, t_b, t_c, t_d, ParameterizedType, \
    t_ref_a, SimpleType
from tests.helpers import assert_let_types


class TestTypeInferer(unittest.TestCase):
    def setUp(self) -> None:
        Args().stop_after_type_inferring = True
        Args().skip_header_generation = True

    def test_simple(self):
        self.assert_types(
            '''
            let f1 = fun(n) -> { if (n = 0) then 1 else n * f1(n - 1) }
            let f2 = fun(a, b, c) -> { a = ""; b = 0; c = b }
            let f3 = fun(a, b, c) -> {
                let d = a = b;
                let e = c -. 0.2;
                a != c 
            }
            ''',
            {
                # int -> int
                'f1': fun_type([t_int], t_int),
                # string -> int -> int -> bool
                'f2': fun_type([t_string, t_int, t_int], t_bool),
                # float -> float -> float -> bool
                'f3': fun_type([t_float, t_float, t_float], t_bool)
            })

    def test_polymorph(self):
        self.assert_types(
            '''
            let f4 = fun(f, x, y) -> { f(x) = y }
            let f5 = fun(x, y, is_q) -> {
                let f = if (is_q) then
                    fun(x) -> { x * x }
                else
                    fun(x) -> { x };
                f4(f, x, y)
            }
            let f6 = fun(f) -> { f4(f, "3", 3) }
            let f7 = fun(f, g, h, x, y) -> { f(g(h(x))) = y }
            let f8 = fun(f, x) -> { f(f(f(x))) }
            let f14: `x -> `x -> `x = fun(a, b) -> { a = a }
            ''',
            {
                # (`a -> `b) -> `a -> `b -> bool
                'f4': fun_type([fun_type([t_a], t_b), t_a, t_b], t_bool),
                # int -> int -> bool -> bool
                'f5': fun_type([t_int, t_int, t_bool], t_bool),
                # (string -> int) -> bool
                'f6': fun_type([fun_type([t_string], t_int)], t_bool),
                # (`a -> `b) -> (`c -> `a) -> (`d -> `c) -> `d -> `b -> bool
                'f7': fun_type([fun_type([t_a], t_b), fun_type([t_c], t_a), fun_type([t_d], t_c), t_d, t_b], t_bool),
                # (`a -> `a) -> `a -> `a
                'f8': fun_type([fun_type([t_a], t_a), t_a], t_a),
                # bool -> bool -> bool
                'f14': fun_type([t_bool, t_bool], t_bool)
            })

    def test_param(self):
        self.assert_types(
            '''
            let f9 = fun(f, v, r) -> {
                let r2 = f(new v);
                (new r2) = $r
            }
            ''',
            # (ref<`a> -> `b) -> `a -> ref<ref<`b>> -> bool
            {'f9': fun_type(
                [fun_type([t_ref_a], t_b), t_a, ParameterizedType('ref', [ParameterizedType('ref', [t_b])])],
                t_bool)})

    def test_type_constructors(self):
        self.assert_types(
            '''
            type a = { f10, f11 = int * float * ref<ref<bool>>, f12 = bool }
            type list<`a> = { Empty, Cons = `a * list<`a> }
            type b<`q> = { f13 = `q * b<b<`q>> }
            ''',
            {
                # a
                'f10': SimpleType('a'),
                # int -> float -> ref<ref<bool>> -> a
                'f11': fun_type([t_int, t_float, ParameterizedType('ref', [ParameterizedType('ref', [t_bool])])],
                                SimpleType('a')),
                # bool -> a
                'f12': fun_type([t_bool], SimpleType('a')),

                # list<`a>
                'Empty': ParameterizedType('list', [t_a]),
                # `a -> list<`a> -> list<`a>
                'Cons': fun_type([t_a, ParameterizedType('list', [t_a])], ParameterizedType('list', [t_a])),

                # `a -> b<b<`a>> -> b<`a>
                'f13': fun_type([t_a, ParameterizedType('b', [ParameterizedType('b', [t_a])])],
                                ParameterizedType('b', [t_a]))
            })

    def test_nested_fun_types(self):
        self.assert_types(
            '''
            let f15 = fun(a, b) -> { a = b }
            let f16 = fun(f, x, y) -> { f(x) = y }
            let f17 = fun(a) -> { f15(a, 0) }
            let f18 = fun(a, b, c) -> { f15(f16(f17, a, b), c) }
            ''',
            {
                # `a -> `a -> bool
                'f15': fun_type([t_a, t_a], t_bool),
                # (`a -> `b) -> `a -> `b -> bool
                'f16': fun_type([fun_type([t_a], t_b), t_a, t_b], t_bool),
                # int -> bool
                'f17': fun_type([t_int], t_bool),
                # int -> bool -> bool -> bool
                'f18': fun_type([t_int, t_bool, t_bool], t_bool)
            })
        pass

    def assert_types(self, code: str, let_names_and_expected_types: dict):
        parse_source_code(f'module test {code}')

        assert_let_types(self, let_names_and_expected_types)


if __name__ == '__main__':
    unittest.main()
