from copy import copy
from typing import List, Optional

from errors import Error, CompilationException
from patterns.singleton import Singleton
from position import Position
from .defs import FakeArg


class RedefinitionException(CompilationException):
    def __init__(self, name, position: Position):
        super().__init__(Error(f"переопределение '{name}'", position))


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


class DefSearchStrategyWithParent(DefSearchStrategy):
    def __init__(self, parent_scope):
        self.parent_scope = parent_scope
        self.do_search_in_parent = True

    def find(self, defs: dict, name: str):
        definition = super().find(defs, name)

        if definition is None and (self.parent_scope is not None) and self.do_search_in_parent:
            defs = self.parent_scope.typedefs if self.is_typedefs else self.parent_scope.lets
            definition = defs.find(name)

        return definition


class Definitions:
    def __init__(self, search_strategy=DefSearchStrategy(), is_typedefs=False):
        self.defs = {}
        self.search_strategy = search_strategy
        self.search_strategy.is_typedefs = is_typedefs

    def add(self, definition, position: Position):
        if self.find(definition.name, True):
            raise RedefinitionException(definition.name, position)

        self.defs[definition.name] = definition

    def find(self, name: str, do_not_use_parent_search=False):
        if isinstance(self.search_strategy, DefSearchStrategyWithParent) and do_not_use_parent_search:
            search_strategy = DefSearchStrategy()
        else:
            search_strategy = self.search_strategy

        return search_strategy.find(self.defs, name)

    def find_or_fail(self, name: str, position: Position):
        definition = self.find(name)
        if definition is None:
            raise NotFoundException(name, position)

        return definition


class Scope:
    def __init__(self, search_strategy=DefSearchStrategy()):
        self.lets = Definitions(search_strategy)
        self.typedefs = Definitions(copy(search_strategy), is_typedefs=True)


class Module:
    def __init__(self, name: str):
        self.name = name
        self.top_scope = Scope()


class GlobalModule(Module, metaclass=Singleton):
    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.top_scope = Scope(DefSearchStrategyForCurrentModule())
        self.included_modules: List[Module] = []
        self.opened_modules: List[Module] = []
