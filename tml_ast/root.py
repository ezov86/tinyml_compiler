from typing import List

from .node import Node
from .import_modules import Import
from position import Position
from .definitions import Definition


class Root(Node):
    def __init__(self, module_name: str, imports: Import, opens: Import, definitions: List[Definition]):
        super().__init__(Position.start())
        self.module_name = module_name
        self.imports = imports
        self.opens = opens
        self.definitions = definitions
