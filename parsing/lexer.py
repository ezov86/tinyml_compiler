import ply.lex as lex
import sys

from errors import CompilationException, Error
from position import Position


class LexException(CompilationException):
    def __init__(self, t):
        super().__init__(Error(f"ошибка в лексеме '{t.value}'", Position.from_lex_token(t)))


# Не знаю что это, но в примерах работы с PLY всегда есть эта строка.
# TODO: попробовать удалить её.
sys.path.insert(0, "../..")

# Имена токенов ключевых слов.
keywords = ('IF', 'TYPE', 'ELSE', 'THEN', 'IMPORT', 'FUN', 'LET', 'OPEN', 'MATCH', 'MODULE', 'NEW')
# Словарь ключевых слов из имен в нижнем регистре (так они выглядят в исходном коде) и имен в верхнем регистре (так их
# типы представляет PLY).
lc_keywords = {x.lower(): x for x in keywords}

# Остальные токены.
tokens = keywords + (
    'PUT', 'ARROW', 'LPAR', 'RPAR', 'EQ', 'NEQ', 'BEQ', 'LEQ', 'COMMA', 'FLOAT_PLUS', 'FLOAT_MINUS', 'FLOAT_MUL',
    'FLOAT_DIV', 'PLUS', 'MINUS', 'MUL', 'DIV', 'MOD', 'GETVAL', 'CONS', 'CONCAT', 'OR', 'AND', 'NOT', 'BOR',
    'BAND', 'BNOT', 'POLYMORPH_TYPE', 'ID', 'INT', 'STR', 'SEMICOLON', 'COLON', 'RSHIFT', 'LSHIFT', 'LANGLE', 'RANGLE',
    'LBRACK', 'RBRACK', 'LBRACE', 'RBRACE', 'FLOAT', 'BIGGER_FLOAT', 'LESS_FLOAT', 'BEQ_FLOAT', 'LEQ_FLOAT')

# Регулярные выражения для остальных токенов.
t_PUT = r'\:\='
t_ARROW = r'\-\>'
t_LPAR = r'\('
t_RPAR = r'\)'
t_EQ = r'\='
t_NEQ = r'\!\='
t_BEQ = r'\>\='
t_LEQ = r'\<\='
t_COMMA = r'\,'
t_FLOAT_PLUS = r'\+\.'
t_FLOAT_MINUS = r'\-\.'
t_FLOAT_MUL = r'\*\.'
t_FLOAT_DIV = r'\/\.'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MUL = r'\*'
t_DIV = r'/'
t_MOD = r'\%'
t_GETVAL = r'\$'
t_CONS = r'\:\:'
t_CONCAT = r'\^'
t_OR = r'\|\|'
t_AND = r'\&'
t_NOT = r'\!'
t_BOR = r'\~\|'
t_BAND = r'\~\&'
t_BNOT = r'\~'
t_SEMICOLON = r'\;'
t_COLON = r'\:'
t_RSHIFT = r'\~\>'
t_LSHIFT = r'\~\<'
t_LANGLE = r'\<'
t_RANGLE = r'\>'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_BIGGER_FLOAT = r'\>\.'
t_LESS_FLOAT = r'\<\.'
t_BEQ_FLOAT = r'\>\=\.'
t_LEQ_FLOAT = r'\<\=\.'

t_INT = r'[0-9]+'
t_FLOAT = r'([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*)'
t_STR = r'\"(?:[^\"\\]|\\.)*\"'
t_POLYMORPH_TYPE = r'[\`][a-z]'


# Переход на новую строку.
def t_NEWLINE(t):
    r"""\n"""
    t.lexer.lineno += 1


# Однострочный комментарий (пока разрешены только такие).
def t_COMMENT(t):
    r"""\#[^\n\r]*"""
    t.lexer.lineno += t.value.count('\n')


# Идентификатор. Если идентификатор есть в таблице ключевых слов в нижнем регистре, то он становится ключевым словом.
def t_ID(t):
    r"""[A-Za-z_]+[\w\._]*"""
    if t.value in lc_keywords:
        t.type = lc_keywords[t.value]

    return t


# Символы, которые можно игнорировать.
t_ignore = '\t \r'


def t_error(t):
    """ Обработчик лексических ошибок. Для продолжения лексического разбора пропускает токен с ошибкой. """
    LexException(t).handle()
    t.lexer.skip(1)


lexer = lex.lex()
