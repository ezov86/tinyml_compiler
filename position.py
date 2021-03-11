class Position:
    def __init__(self, line: int):
        self.line = line

    @staticmethod
    def start():
        return Position(1)

    @staticmethod
    def from_parser_ctx(p):
        return Position(p.slice[1].lineno)
