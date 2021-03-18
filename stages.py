import argparse
import json

from args import Args
from ast_to_dict_visitor import AstToDictVisitor
from base_stage import *
from parsing.parser import parser
from semantic.ast_visitor import SemanticVisitor
from semantic.builtins import builtin_types


class ArgumentParsingStage(BaseStage):
    def handle(self, result):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('source', help='Путь к файлу с исходным кодом.')
        arg_parser.add_argument('-p', '--stop-after-parsing',
                                help='Остановиться после синтаксического анализа и вывести АСД в виде JSON.',
                                action='store_true')

        args = arg_parser.parse_args()
        Args().initialize(args)
        return super().handle(result)


class SourceCodeReadingStage(BaseStage):
    def handle(self, result):
        with open(Args().source, 'r') as file:
            text = file.read()

        return super().handle(text)


class ParsingStage(BaseStage):
    def handle(self, result):
        ast = parser.parse(result, tracking=True)

        if Args().stop_after_parsing and Errors().is_ok():
            print(json.dumps(AstToDictVisitor().visit(ast)))
            exit(0)

        return super().handle(ast)


class AstVisitingStage(BaseStage):
    def handle(self, result):
        return super().handle(SemanticVisitor().visit_root(result, [builtin_types]))


class TypeInferringStage(BaseStage):
    def handle(self, result):
        return super().handle(result)


class OptimizationStage(BaseStage):
    def handle(self, result):
        return super().handle(result)


class CodeGenerationStage(BaseStage):
    def handle(self, result):
        return super().handle(result)
