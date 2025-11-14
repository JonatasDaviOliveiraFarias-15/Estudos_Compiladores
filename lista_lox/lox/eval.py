from multiprocessing import Value
from lox.errors import LoxRuntimeError
from lox.tokens import Token

def check_number_operands(operator: Token,
                          left: Value,
                          right: Value):
    if isinstance(left, float) and isinstance(right, float):
        return
    raise LoxRuntimeError("Operands must be numbers.", operator)