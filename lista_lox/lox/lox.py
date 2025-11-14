import tokenize
from typing import Self
from lox.parser import parse
from lox.ast_printer import pretty

tokens = tokenize(Self.source)
expression = parse(tokens)
if expression is None:
    pass
else:
    print(pretty(expression))