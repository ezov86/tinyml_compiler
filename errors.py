from typing import Optional, List

from args import Args
from patterns.singleton import Singleton
from position import Position


class Error:
    def __init__(self, message: str, position: Optional[Position] = None):
        self.message = message + '.'
        self.position = position

    def __str__(self) -> str:
        pos = '' if self.position is None else f':{self.position.line}'
        return f'{Args().source}{pos}: {self.message}'


class Errors(metaclass=Singleton):
    list: List[Error] = []

    def is_ok(self):
        return len(self.list) == 0


class CompilationException(Exception):
    def __init__(self, error: Error):
        self.error = error

    def handle(self):
        Errors().list.append(self.error)

    def __str__(self) -> str:
        return str(self.error)
