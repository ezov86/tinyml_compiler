from typing import List

from error import Error


class StageResult:
    def __init__(self, args=None, data=None, errors: List[Error] = []):
        self.args = args
        self.data = data
        self.errors = errors

    def is_ok(self) -> bool:
        return self.errors == []


class BaseStage:
    def __init__(self):
        self.next = None

    def set_next(self, next_stage):
        self.next = next_stage

        return next_stage

    def handle(self, prev_stage_result: StageResult) -> StageResult:
        if not prev_stage_result.is_ok():
            for error in prev_stage_result.errors:
                print(error)

        if self.next is None or not prev_stage_result.is_ok():
            return prev_stage_result

        return self.next.handle(prev_stage_result)
