import argparse
import json
from pathlib import Path

from args import Args
from ast_to_dict_visitor import AstToDictVisitor
from errors import Errors
from header_gen import HeaderGenerator
from parsing.parser import parser
from semantic.ast_visitor import SemanticVisitor
from semantic.typing.inferer import GlobalTypeInferer
from tml_ast import Root


def handle_next_stage(result, next_stage=None):
    if not Errors().is_ok():
        for error in Errors().list:
            print(error)

        exit(-1)

    if next_stage is None:
        return result

    return next_stage(result)


def parse_args(_=None):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('source', help='Путь к файлу с исходным кодом.')
    arg_parser.add_argument('-p', '--stop-after-parsing',
                            help='Остановиться после синтаксического анализа и вывести АСД в виде JSON.',
                            action='store_true')
    arg_parser.add_argument('-g', '--skip-header-generation', help='Пропустить генерацию заголовочного файла модуля.',
                            action='store_true')

    args = arg_parser.parse_args()
    Args(args)

    return handle_next_stage(None, read_source_code)


def read_source_code(_):
    with open(Args().source, 'r') as file:
        text = file.read()

    return handle_next_stage(text, parse_source_code)


def parse_source_code(text: str):
    ast = parser.parse(text, tracking=True)
    if Args().stop_after_parsing and Errors().is_ok():
        print(json.dumps(AstToDictVisitor().visit(ast)))
        exit(0)

    return handle_next_stage(ast, visit_ast)


def visit_ast(ast: Root):
    module = SemanticVisitor().visit_root(ast)
    return handle_next_stage(module, infer_types)


def infer_types(module):
    GlobalTypeInferer().infer()
    return handle_next_stage(module, generate_header)


def generate_header(module):
    if not Args().skip_header_generation:
        text = json.dumps(HeaderGenerator().visit(module), separators=(',', ':'))
        with Path(Args().source).with_suffix('').open('w') as file:
            file.write(text)

    return handle_next_stage(module, generate_code)


def generate_code(module):
    return handle_next_stage(None)


if __name__ == '__main__':
    parse_args()

