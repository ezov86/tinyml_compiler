from base_stage import *
import argparse
from parsing.parser import parser


class ArgumentParsingStage(BaseStage):
    def handle(self, result: StageResult) -> StageResult:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument('source', help='Путь к файлу с исходным кодом.')

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
