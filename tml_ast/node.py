from typing import Any

from position import Position
from .visitor import Visitor


class Node:
    def __init__(self, position: Position):
        self.position = position

    def accept(self, visitor: Visitor) -> Any:
        pass
