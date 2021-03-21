# tinyml_compiler

Компилятор для простого функционального ЯП.

Работа над ним ведется в рамках прикладного проекта для научно-практической конференции
"День Науки и творчества 2021" и для городской научно-практической конференции школьников «ИНТЕЛЛЕКТУАЛ» г. Кемерово.

Цель проекта: создание простого языка и компилятора для него с целью приобретения опыта и создания наглядного примера с пояснениями.

## Зависимости

[PLY](https://github.com/dabeaz/ply)

[llvmlite](https://github.com/numba/llvmlite)

[inflection](https://pypi.org/project/inflection)

[Python 3.8+](https://www.python.org/downloads/release/python-380) (должно работать и на версии 3.6)

## Описание языка

[Грамматика языка](https://github.com/mahintim2/tinyml_compiler/blob/master/docs/grammar.md)

## Запуск

В source.tml исходный код:
``` python3 main.py source.tml ```

Для получения помощи по использованию:
``` python3 main.py -h ```
