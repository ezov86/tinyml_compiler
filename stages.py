import json

from ast_to_dict_visitor import AstToDictVisitor
from base_stage import *
import argparse
from parsing.parser import parser
from tml_ast.node import to_json as ast_to_json


class ArgumentParsingStage(BaseStage):
    def handle(self, result: StageResult) -> StageResult:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('source', help='Путь к файлу с исходным кодом.')
        arg_parser.add_argument('-p', '--stop-after-parse',
                                help='Остановиться после синтаксического анализа и вывести АСД в виде JSON.',
                                action='store_true')

        args = arg_parser.parse_args()
        return super().handle(StageResult(args=args))


class SourceCodeReadingStage(BaseStage):
    def handle(self, result: StageResult) -> StageResult:
        with open(result.args.source, 'r') as file:
            text = file.read()

        return super().handle(StageResult(args=result.args, data=text))


class ParsingStage(BaseStage):
    def handle(self, result: StageResult) -> StageResult:
        ast = parser.parse(result.data, tracking=True)

        if result.args.stop_after_parse:
            print(json.dumps(AstToDictVisitor().visit(ast)))

        return super().handle(StageResult(args=result.args, data=ast))


class AstVisitingStage(BaseStage):
    def handle(self, prev_stage_result: StageResult) -> StageResult:
        return super().handle(prev_stage_result)


class TypeInferringStage(BaseStage):
    def handle(self, prev_stage_result: StageResult) -> StageResult:
        return super().handle(prev_stage_result)


class OptimizationStage(BaseStage):
    def handle(self, prev_stage_result: StageResult) -> StageResult:
        return super().handle(prev_stage_result)


class CodeGenerationStage(BaseStage):
    def handle(self, prev_stage_result: StageResult) -> StageResult:
        return super().handle(prev_stage_result)
