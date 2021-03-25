from itertools import zip_longest
from typing import List

from errors import CompilationException, Error
from patterns.singleton import Singleton
from position import Position
from semantic.typing.global_to_local import GlobalToLocalTypeVisitor
from semantic.typing.polym_type_name_setter import PolymorphTypeNameSetter
from semantic.typing.types import is_polymorph_t, is_param_t


class TypesNotCompatibleException(CompilationException):
    def __init__(self, t1, t2, position: Position):
        super().__init__(Error(f'тип {t1} несовместим с типом {t2}', position))


class TypeWrapper:
    def __init__(self, t, do_replace_globals_with_locals=False):
        self.type = t
        self.do_replace_globals_with_locals = do_replace_globals_with_locals

        GlobalTypeInferer().type_wrappers.append(self)

    def replace_type(self, original, new):
        self.type.replace_type(original, new)

        if self.type == original:
            self.type = new


class TypeInferer:
    def __init__(self):
        self.constraints = []
        self.type_wrappers: List[TypeWrapper] = []

    def infer(self):
        for constraint in self.constraints:
            if is_param_t(constraint.left) and is_param_t(constraint.right) and \
                    not constraint.is_converted_to_simple_constraints:
                # Иногда при создании ограничения один или оба типа являются полиморфными, но когда вывод доходит до
                # них, то они могут состоять из двух параметрических типов, в таком случая необходимо создать новое
                # ограничение на основе данного и обработать именно новое.
                constraint = self.recreate_constraint(constraint)

            constraint.unify()

    def recreate_constraint(self, constraint):
        """
        Возвращает новое ограничения на основе данного (причину см. в infer() и Constraint.__init__()).
        """
        # TODO: см. комментарий к Constraint.__init__.
        return Constraint(constraint.left_wrapper,
                          constraint.right_wrapper,
                          constraint.expression,
                          constraint.do_use_local_inferer,
                          constraint.local_inferer,
                          constraint.not_part_of_global,
                          is_first_local_constraint=True,
                          args=constraint.args,
                          replace_right_globals=constraint.replace_right_globals)

    def replace_type(self, original, new):
        if original == new:
            return

        for wrapper in self.type_wrappers:
            wrapper.replace_type(original, new)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

        # self.type_wrappers.append(constraint.left_wrapper)
        # self.type_wrappers.append(constraint.right_wrapper)

    def dump(self) -> str:
        ns = PolymorphTypeNameSetter()
        return '\n'.join([constraint.dump(ns) for constraint in self.constraints])


class GlobalTypeInferer(TypeInferer, metaclass=Singleton):
    """ Синглтон, глобальный вывод типов. """

    def __init__(self):
        super().__init__()

    def replace(self, original, new):
        super().replace_type(original, new)

        # Замена типа в локальных выводах типов.
        for constraint in self.constraints:
            if constraint.do_use_local_inferer:
                constraint.local_inferer.replace_type(original, new, do_not_replace_in_global=True)


class LocalTypeInferer(TypeInferer):
    """ Локальный вывод типов. """

    def __init__(self, first_local_constraint):
        super().__init__()
        self.first_local_constraint = first_local_constraint

    def global_to_locals(self):
        visitor = GlobalToLocalTypeVisitor()

        for constraint in self.constraints:
            # TODO: без not_part_of_global все тесты проходятся успешно. Возможно что-то без этого работать не будет.
            #   Попробовать найти такой случай, добавить его в тесты и раскомментировать эти строки, иначе убрать из
            #   Constraint.

            # if constraint.not_part_of_global:
            #     continue

            constraint.left = visitor.visit(constraint.left)

            if constraint.replace_right_globals:
                constraint.right = visitor.visit(constraint.right)

    def recreate_constraint(self, constraint):
        # Отличие от TypeInferer.recreate_constraint() в том, что здесь ограничение всегда не являются первыми
        # локальными, а типы всегда сохранены в локальном выводе.
        return Constraint(constraint.left_wrapper,
                          constraint.right_wrapper,
                          constraint.expression,
                          constraint.do_use_local_inferer,
                          constraint.local_inferer,
                          constraint.not_part_of_global,
                          is_first_local_constraint=False,
                          args=constraint.args,
                          replace_right_globals=constraint.replace_right_globals)

    def infer(self):
        self.global_to_locals()
        super().infer()

    def replace_type(self, original, new, do_not_replace_in_global=False):
        super().replace_type(original, new)

        if not do_not_replace_in_global:
            GlobalTypeInferer().replace_type(original, new)


class Constraint:
    """ Ограничение, тождество типов. """

    def __init__(self, left_wrapper: TypeWrapper, right_wrapper: TypeWrapper, expression,
                 do_use_local_inferer=False, local_inferer=None, not_part_of_global=False,
                 is_first_local_constraint=False, args=[], replace_right_globals=False):
        # TODO: конструктор имеет слишком большое количество аргументов. Один из вариантов решения: использовать паттерн
        #  "строитель".
        self.not_part_of_global = not_part_of_global

        self.expression = expression

        self.do_use_local_inferer = do_use_local_inferer
        self.local_inferer = local_inferer

        self.left_wrapper = left_wrapper
        self.right_wrapper = right_wrapper

        self.is_first_local_constraint = is_first_local_constraint
        self.args = args
        self.replace_right_globals = replace_right_globals

        # Определение текущего вывода типов.
        if self.do_use_local_inferer:
            if self.local_inferer is None:
                # Это тождество параметрических типов, необходимо создать новый локальные вывод типов.
                # Оно также является первым локальным.
                self.is_first_local_constraint = True
                self.local_inferer = LocalTypeInferer(self)

            self.cur_inferer = self.local_inferer
        else:
            self.cur_inferer = GlobalTypeInferer()

        self.is_converted_to_simple_constraints = False
        self.param_to_simple_constraints()

    def param_to_simple_constraints(self):
        """
        Преобразует тождество из двух параметрических типов в тождества каждых соответствующих типов параметров.
        """
        if is_param_t(self.left) and is_param_t(self.right):
            # Если оба типа являются параметрическими, то добавить в текущий вывод типов тождества каждых
            # соответствующих типов-параметров.
            for p_left, p_right, arg in zip_longest(self.left.params, self.right.params, self.args):
                if arg is not None:
                    replace_right_globals = arg.is_const_fun()
                else:
                    replace_right_globals = self.replace_right_globals

                constraint = Constraint(TypeWrapper(p_left), TypeWrapper(p_right), self.expression,
                                        do_use_local_inferer=self.do_use_local_inferer, local_inferer=self.cur_inferer,
                                        not_part_of_global=not self.is_first_local_constraint,
                                        replace_right_globals=replace_right_globals)

                self.cur_inferer.constraints.append(constraint)

            self.is_converted_to_simple_constraints = True

    def unify(self):
        if not self.left.is_compatible(self.right):
            name_setter = PolymorphTypeNameSetter()
            name_setter.visit(self.left)
            name_setter.visit(self.right)

            raise TypesNotCompatibleException(self.left, self.right, self.expression.position)

        if self.do_use_local_inferer and self.is_first_local_constraint:
            # Это первое тождество с локальным выводом типов, значит необходимо провести этот вывод.
            # Может сложиться такая ситуация, что is_first_local_constraint == True, а текущий вывод типов является
            # глобальным, поэтому необходимо также проверить на то, используется ли именно локальный вывод типов,
            # иначе в некоторых случаях будет бесконечная рекурсия (например: let f = fun(f) -> {f(f(x))}).
            self.cur_inferer.infer()
        elif not (is_param_t(self.left) and is_param_t(self.right)):
            original, new = self.get_original_and_new()
            self.cur_inferer.replace_type(original, new)

    def get_original_and_new(self):
        """ Возвращает кортеж из двух типов, первый из которых будет заменен на второй """
        # Этот метод будет вызван только в случае если оба типа полиморфны или один полиморфный, а другой - простой или
        # параметрический.
        if is_polymorph_t(self.left):
            # Если левый является полиморфным, то он будет заменен первым.
            return self.left, self.right
        else:
            # Иначе полиморфным является правый или они оба полиморфны и порядок замены не имеет значения.
            return self.right, self.left

    def get_left(self):
        return self.left_wrapper.type

    def set_left(self, t):
        self.left_wrapper.type = t

    def set_right(self, t):
        self.right_wrapper.type = t

    def get_right(self):
        return self.right_wrapper.type

    def dump(self, ns: PolymorphTypeNameSetter) -> str:
        ns.visit(self.left)
        ns.visit(self.right)

        expr = self.expression.__class__.__name__

        if hasattr(self.expression, 'name'):
            expr += f" '{self.expression.name}'"
        elif hasattr(self.expression, 'fun') and hasattr(self.expression.fun, 'let'):
            expr += f" '{self.expression.fun.let.name}'"

        return f'line {self.expression.position} {"*" if self.do_use_local_inferer else ""} {expr}\n\t{self.left} =' \
            f'{self.right} '

    left = property(get_left, set_left)
    right = property(get_right, set_right)
