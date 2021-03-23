import json
import unittest

from args import Args
from header_gen import HeaderGenerator
from header_reader import HeaderReader
from main import parse_source_code
from semantic.module import GlobalModule


class TestHeader(unittest.TestCase):
    def setUp(self) -> None:
        Args().skip_header_generation = True
        Args().skip_code_generation = True

    def test_header_to_json_and_back(self):
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
                    let d = fun() -> { let a = 4; a + 4 }'''

        parse_source_code(code)
        dic = HeaderGenerator().visit(GlobalModule())
        module2 = HeaderReader().read_module(dic)
        dic2 = HeaderGenerator().visit(module2)

        self.assertEqual(json.dumps(dic), json.dumps(dic2)),


if __name__ == '__main__':
    unittest.main()
