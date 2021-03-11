from position import Position


class Error:
    def __init__(self, position: Position, message: str):
        self.position = position
        self.message = message
