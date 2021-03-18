# Грамматика TinyML

В этом файле находится описание грамматики TinyML для LALR(1) парсера.

Синтаксис описания правил:
* () — группировка.
* ? — 0 или 1 повторение.
* \* — 0 и более повторений.
* \+ — одно и более повторение.
* regex(x) — регулярное выражение PCRE x. 
* x — нетерминал с именем x.
* X — терминал с именем x.
* a | b — a или b.
* 'x' — токен x.


### Верхний уровень (модуль) 
```
module = 'module' ID import? open_or_none? defs_or_none?

open = 'open' modules_list
import = 'import' modules_list
modules_list = str (',' modules_list)*
                    
defs = def+
       
def = let
    | type_def
      
let = 'let' ID type_hint? '=' expr
                      
type_hint = ':' type

type_def = 'type' ID polymorph_type_params? '=' '{' type_constructors '}'

polymorph_type_params = '<' polymorph_types_list '>'

polymorph_types_list = polymorph_type (',' polymorph_types_list)* 
                       
type_constructors = type_constructor
                  | type_constructor ',' type_constructors
                  | ID types_product_or_none
                    
types_product_or_none = empty
                      | types_product_with_eq

types_product_with_eq = '=' types_product

types_product = type ('*' types_product)*

```

### Типы
```

type = atomic_type
type = fun_type

atomic_type = simple_type
            | param_type
            | polymorph_type
            | type_in_par

simple_type = ID
param_type = ID '<' types_list '>'
types_list = type (',' types_list)*

fun_type = fun_type_arg
         | fun_type_args

fun_type_arg = '->' single_type_to_list
single_type_to_list = atomic_type
fun_type_args = atomic_type '->' right_arg_type

right_arg_type = fun_type_args
               | single_type_to_list
               
polymorph_type = POLYMORPH_TYPE

type_in_par = '(' type ')'
```

### Выражения
```
expr = const
     | var
     | if
     | group
     | apply
     | match
     | fun
     | bin_op
     | un_op
     | list
     | get_el

bin_op = expr ':=' expr
       | expr '=' expr
       | expr '<' expr
       | expr '>' expr
       | expr '<.' expr
       | expr '>.' expr
       | expr '!=' expr
       | expr '>=' expr
       | expr '<= expr
       | expr '>=.' expr
       | expr '<=.' expr
       | expr '+.' expr
       | expr '-.' expr
       | expr '*.' expr
       | expr '/.' expr
       | expr '+' expr
       | expr '-' expr
       | expr '*' expr
       | expr '/' expr
       | expr '%' expr
       | expr '::' expr
       | expr '^' expr
       | expr '|' expr
       | expr '&' expr
       | expr '~|' expr
       | expr '~&' expr
       | expr '>>' expr
       | expr '<<' expr
       
un_op = '!' expr
      | '-' expr
      | '-.' expr
      | '~' expr
      | 'new' expr
      | '$' expr
      
list = '[' expr_comma_list? ']'

get_el = list_expr '[' expr ']'

list_expr = group
          | apply
          | get_el
          | var
          | list

group = '(' expr ')'

var = ID

if = 'if' group 'then' expr 'else' expr

apply = applicable_expr '(' expr_comma_list? ')'

match = 'match' expr '{' match_branch (,' match_branches)* '}'

match_branch = expr '->' match_branch_body

match_branch_body = expr
                  | match_branch_body_expr_group
                  
match_branch_body_expr_group = '{' expr_semicolon_list '}'

expr_semicolon_list = expr (';' expr_semicolon_list)*

applicable_expr = group
                | apply
                | var
                 
expr_comma_list = expr (',' expr_comma_list)*

fun = 'fun' '(' args_list? ')' '->' '{' fun_body '}'

args_list = ID (',' args_list)*

fun_body = fun_body_stmt
         | fun_body_stmt SEMICOLON fun_body

fun_body_stmt = expr
              | let

const = str_const
      | int_const
      | float_const
      | unit
      
str_const = STR
int_const = INT
float_const = FLOAT
unit = '(' ')'
```

### Терминалы
```
INT = regex([0-9]+)
FLOAT = regex(([0-9]*\.[0-9]+)|([0-9]+\.[0-9]*))
STR = regex(\"(?:[^\"\\]|\\.)*\")
POLYMORPH_TYPE = regex([\`][a-z])
ID = regex([A-Za-z_]+[\w\._]*)
```

### Игнорируемые символы
```
IGNORE = regex((\#[^\n\r]*)|[\n\r \t])
```

## Таблица приоритетов:
| Операция | Приоритет (большее число — больший приоритет) |
| -------- | --------- |
| := | 0 |
| new | 1 |
| then else | 2 |
| &#124; | 3 |
| & | 4 |
| = != > < <= >= >. <. >=. <=. | 5 |
| ^ :: | 6 |
| >> << | 7 |
| + - +. -. | 8 |
| * / % *. /. | 9 |
| унарные операторы: - ! $ ~ | 10 |
