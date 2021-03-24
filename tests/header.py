import json
import unittest
from typing import Dict

from args import Args
from header_gen import HeaderGenerator
from header_reader import HeaderReader
from main import parse_source_code
from semantic.module import GlobalModule
from os import remove as remove_file

from semantic.typing.inferer import GlobalTypeInferer
from semantic.typing.types import fun_type, t_int, t_bool, t_a, t_b, t_c
from tests.helpers import assert_let_types


class TestHeader(unittest.TestCase):

    def setUp(self) -> None:
        Args().__init__()
        Args().skip_code_generation = True

        self.reset_module()

    def reset_module(self):
        GlobalModule().__init__()

    def test_header_to_json_and_back(self):
        Args().skip_header_generation = True

        code = '''  module test
        
                    type list<`a> = {
                       Empty,
                       Cons = `a * list<`a>
                    }
                    
                    type a<`x, `y> = {
                       B = ref<ref<ref<`x>>> * `y * `x * ref<ref<ref<`y>>>,
                       A = a<bool, a<int, float>>
                    }
                    
                    let a: `a -> `a -> bool = fun(a, b) -> {True}
                    let b = fun(f, x, y) -> {f(x) = y}
                    let c: string -> a<int, string> -> unit = fun(p, q) -> {()}
                    let d = fun() -> { let a = 4; a + 4 }
                    
                    let foo = fun(a, b) -> { a + b }
                    let bar = fun(a, b) -> { foo(a, b) != 0 }
                    let baz = fun(f, x, y) -> { f(x) = y }'''

        parse_source_code(code)
        dic = HeaderGenerator().visit(GlobalModule())
        module2 = HeaderReader().read_module(dic)
        dic2 = HeaderGenerator().visit(module2)

        self.assertEqual(json.dumps(dic), json.dumps(dic2))

    def test_header_inclusion(self):
        self.reset_module()

        a_code = '''module a
        
                    type a<`a, `b> = {
                        A,
                        B,
                        C = `a * `b,
                        D = a<`a, a<bool, string>> * `b
                    }
                    
                    let foo = fun(a, b) -> { a + b }
                    let bar = fun(a, b) -> { foo(a, b) != 0 }
                    let baz = fun(f, x, y) -> { f(x) = y } '''
        b_code = '''module b

                    type b<`a> = {
                        A,
                        B = `a * int
                    }

                    let foo = fun(a, b) -> { a = b }
                    let bar = fun(a) -> { foo(a, 0) }
                    let baz = fun(f, g, x) -> { f(g(x)) }'''
        c_code = '''module c

                    import "a"
                    open "b"

                    let test1 = fun(a, b, c) -> { foo(a.baz(bar, a, b), c) }
                    let test2 = baz
                    let test3 = a.bar'''

        Args().source = 'a.tml'
        parse_source_code(a_code)
        self.reset_module()

        Args().source = 'b.tml'
        parse_source_code(b_code)
        self.reset_module()

        Args().source = 'c.tml'
        Args().skip_header_generation = True
        parse_source_code(c_code)

        assert_let_types(self, {
            'test1': fun_type([t_int, t_bool, t_bool], t_bool),
            'test2': fun_type([fun_type([t_a], t_b), fun_type([t_c], t_a), t_c], t_b),
            'test3': fun_type([t_int, t_int], t_bool)
        })


if __name__ == '__main__':
    unittest.main()
