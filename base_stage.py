from errors import Errors


class BaseStage:
    def __init__(self):
        self.next = None

    def set_next(self, next_stage):
        self.next = next_stage
        return next_stage

    def handle(self, prev_result) -> any:
        if not Errors().is_ok():
            for error in Errors().list:
                print(error)

            exit(-1)

        if self.next is None:
            return prev_result

        return self.next.handle(prev_result)
