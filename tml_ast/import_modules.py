from typing import List

from .node import Node
from position import Position


class Import(Node):
    def __init__(self, position: Position, modules: List[str], do_open_namespace=False):
        super().__init__(position)
        self.modules = modules
        self.do_open_namespace = do_open_namespace
