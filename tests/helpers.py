from position import Position
from semantic.module import GlobalModule
from semantic.typing.polym_type_name_setter import PolymorphTypeNameSetter


def assert_let_types(unit_test, let_names_and_expected_types: dict):
    for let_name, expected_type in let_names_and_expected_types.items():
        actual = GlobalModule().top_scope.lets.find_or_fail(let_name, Position.start()).type

        PolymorphTypeNameSetter().visit(expected_type)
        PolymorphTypeNameSetter().visit(actual)

        unit_test.assertEqual(f'{let_name}: {expected_type}', f'{let_name}: {actual}')
