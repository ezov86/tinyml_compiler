import sys

from stages import *

first_stage = ArgumentParsingStage()

first_stage \
    .set_next(SourceCodeReadingStage()) \
    .set_next(ParsingStage()) \
    .set_next(AstVisitingStage()) \
    .set_next(TypeInferringStage()) \
    .set_next(OptimizationStage()) \
    .set_next(CodeGenerationStage())

final_result = first_stage.handle(sys.argv)
exit(0)
