from typing import List

from errors import Error, CompilationException
from patterns.singleton import Singleton
from position import Position
from .defs import FakeArg
from .node import Node


class RedefinitionException(CompilationException):
    def __init__(self, name):
        super().__init__(Error(f"переопределение '{name}'"))


class NotFoundException(CompilationException):
    def __init__(self, name, position: Position):
        super().__init__(Error(f"'{name}' не определено в текущей области видимости", position))


class DefSearchStrategy:
    """ Обычная стратегия поиска объявлений модуля (используется для внешних модулей и как основа для стратегии поиска
    из текущего модуля). """

    # Является ли искомое определение определением типа.
    is_typedefs = False

    def find(self, defs: dict, name: str):
        if name not in defs:
            return None

        if isinstance(defs[name], FakeArg):
            # Фейковые аргументы не имеют уникальных имен, поэтому их искать не нужно.
            return None

        return defs[name]


class DefSearchStrategyForCurrentModule(DefSearchStrategy):
    """ Стратегия поиска объявления в текущем модуле.  """

    def find(self, defs: dict, name: str):
        if '.' not in name:
            definition = super().find(defs, name)
            if definition is not None:
                return definition

            for module in GlobalModule().opened_modules:
                defs = module.top_scope.typedefs if self.is_typedefs else module.top_scope.lets
                definition = defs.find(name)

                if definition is not None:
                    return definition

            return None
        else:
            splitted_name = name.split('.')
            module_name, def_name = '.'.join(splitted_name[:-1]), splitted_name[-1]

            module = module_name not in GlobalModule().included_modules
            if module is None:
                return None

            defs = module.top_scope.typedefs if self.is_typedefs else module.top_scope.lets
            return defs.find(def_name)


class Definitions:
    def __init__(self, search_strategy, is_typedefs=False):
        self.defs = {}
        self.search_strategy = search_strategy
        self.search_strategy.is_typedefs = is_typedefs

    def add(self, definition):
        if self.find(definition.name):
            raise RedefinitionException(definition.name)

        self.defs[definition.name] = definition

    def find(self, name: str):
        return self.search_strategy.find(self.defs, name)

    def find_or_fail(self, name: str, position: Position):
        definition = self.find(name)
        if definition is None:
            raise NotFoundException(name, position)

        return definition


class Scope:
    def __init__(self, search_strategy=DefSearchStrategy()):
        self.lets = Definitions(search_strategy)
        self.typedefs = Definitions(search_strategy, is_typedefs=True)


class Module:
    def __init__(self, name: str):
        self.name = name
        self.top_scope = Scope()


class GlobalModule(Module, Singleton):
    # Здесь для инициализации не используется обычный конструктор из-за ограничений реализации паттерна синглтона.
    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    # noinspection PyAttributeOutsideInit
    def init(self, name: str):
        self.name = name
        self.top_scope = Scope(DefSearchStrategyForCurrentModule())
        self.included_modules: List[Module] = []
        self.opened_modules: List[Module] = []
