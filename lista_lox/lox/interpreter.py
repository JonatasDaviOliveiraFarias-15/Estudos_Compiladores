from ast import For
from functools import singledispatch
from multiprocessing import Value
from lox.ast import *
from lox.eval import check_number_operands
from lox.tokens import TokenType
from lox.tokens import Token
from lox.errors import LoxRuntimeError
from lox import env

class Env(env.Env[Value]):
    pass

@singledispatch
def eval(expr: Expr, env: Env) -> Value: 
    msg = f"cannot eval {expr.__class__.__name__} objects"
    raise TypeError(msg)

@eval.register
def _(expr: Literal, env: Env) -> Value:
    return expr.value

@eval.register
def _(expr: Grouping, env: Env) -> Value:
    return eval(expr.expression, env)

@eval.register
def _(expr: Unary, env: Env) -> Value:
    right = eval(expr.right, env)
    match expr.operator.type :
        case "MINUS":
            return -as_number_operand(expr.operator, right)
        case "BANG":
            return not is_truthy(right)
        case op:
            assert False, f"unhandled operator {op}"

def is_truthy(obj: Any) -> bool:
    if obj is None or obj is False:
        return False
    return True

@eval.register
def _(expr: Binary, env: Env) -> Value:
    left = eval(expr.left, env)
    right = eval(expr.right, env)
    match expr.operator.type:
        case "BANG_EQUAL":
            return not is_equal(left, right)
        case "EQUAL_EQUAL":
            return is_equal(left, right)
        case "GREATER":
            check_number_operands(expr.operator, left, right)
            return left > right
        case "GREATER_EQUAL":
            check_number_operands(expr.operator, left, right)
            return left >= right
        case "LESS":
            check_number_operands(expr.operator, left, right)
            return left < right
        case "LESS_EQUAL":
            check_number_operands(expr.operator, left, right)
            return left <= right
        case "MINUS":
            check_number_operands(expr.operator, left, right)
            return left - right
        case "SLASH":
            check_number_operands(expr.operator, left, right)
            return divide(left, right)
        case "STAR":
            check_number_operands(expr.operator, left, right)
            return left * right
        case "PLUS":
            if isinstance(left, (float, int)) and isinstance(right, (float, int)):
                return left + right
            if isinstance(left, str) or isinstance(right, str):
                return stringify(left) + stringify(right)
            msg = "Operands must be two numbers or two strings."
            raise LoxRuntimeError(msg, expr.operator)
        case op:
            assert False, f"unhandled operator {op}"

def divide(left: float, right: float) -> float:
    if right != 0:
        return left / right
    if left == 0:
        return float("nan")
    elif left > 0:
        return float("inf")
    else:
        return float("-inf")
    
def is_equal(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) == type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b
    if isinstance(a, str) and isinstance(b, str):
        return a == b
    return a is b

def as_number_operand(operator: Token, operand: Value) -> float:
    if isinstance(operand, (float, int)):
        return float(operand)
    raise LoxRuntimeError("Operand must be a number.", operator)

def stringify(value: Value) -> str:
    if value is None:
        return "nil"
    elif isinstance(value, float):
        return str(value).removesuffix(".0")
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return str(value)
    
@singledispatch
def exec(stmt: Stmt, env: Env) -> None:
    msg = f"exec not implemented for {type(stmt)}"
    raise TypeError(msg)

@exec.register
def _(stmt: Expression, env: Env) -> None:
    eval(stmt.expression, env)

@exec.register
def _(stmt: Print, env: Env) -> None:
    value = eval(stmt.expression, env)
    print(stringify(value))

@exec.register
def _(stmt: Program, env: Env) -> None:
    for child in stmt.statements:
        exec(child, env)

@exec.register
def _(stmt: Var, env: Env) -> None:
    value = eval(stmt.initializer, env) if stmt.initializer is not None else None
    env[stmt.name.lexeme] = value

@eval.register
def _(expr: Variable, env: Env) -> Value:
    try:
        return env[expr.name.lexeme]
    except NameError as error:
        msg = f"Undefined variable '{expr.name.lexeme}'."
        raise LoxRuntimeError(msg, expr.name)
    
@eval.register
def _(expr: Assign, env: Env) -> Value:
    value = eval(expr.value, env)
    try:
        env.assign(expr.name.lexeme, value)
    except NameError as error:
        msg = f"Undefined variable '{expr.name.lexeme}'."
        raise LoxRuntimeError(msg, expr.name)
    return value

@exec.register
def _(stmt: Block, env: Env) -> None:
    inner_env = env.push() 
    for statement in stmt.statements:
        exec(statement, inner_env)

@exec.register
def _(stmt: If, env: Env) -> None:
    condition = eval(stmt.condition, env)
    if is_truthy(condition):
        exec(stmt.then_branch, env)
    elif stmt.else_branch is not None:
        exec(stmt.else_branch, env)

@eval.register
def _(expr: Logical, env: Env) -> Value:
    left = eval(expr.left, env)
    if expr.operator.type == "OR":
        if is_truthy(left):
            return left
    elif expr.operator.type == "AND":
        if not is_truthy(left):
            return left
    return eval(expr.right, env)

@exec.register
def _(stmt: While, env: Env) -> None:
    while is_truthy(eval(stmt.condition, env)):
        exec(stmt.body, env)

@exec.register
def _(stmt: For, env: Env) -> None:
    statements = []
    if stmt.initializer is not None:
        statements.append(stmt.initializer)
    while_body = [stmt.body]
    if stmt.increment is not None:
        while_body.append(Expression(stmt.increment))
    if stmt.condition is None:
        condition = Literal(True)
    else:
        condition = stmt.condition
    while_stmt = While(condition, Block(while_body))
    statements.append(while_stmt)
    exec(Block(statements), env)

class Class:
    def __init__(self, name: str):
        self.name = name
        self.methods = {}

    def call(self, interpreter, arguments):
        return Instance(self)

    def arity(self):
        return 0

    def __repr__(self):
        return f"<class {self.name}>"
    
@exec.register
def _(stmt: ClassStmt, env: Env) -> None:
    klass = Class(stmt.name.lexeme)
    env[stmt.name.lexeme] = klass

@eval.register(Call)
def _(expr: Call, env: Env):
    callee = eval(expr.callee, env)
    arguments = [eval(arg, env) for arg in expr.arguments]
    if not hasattr(callee, "call"):
        raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
    if hasattr(callee, "arity") and len(arguments) != callee.arity():
        raise LoxRuntimeError(
            expr.paren,
            f"Expected {callee.arity()} arguments but got {len(arguments)}."
        )
    return callee.call(interpreter=None, arguments=arguments)

class Instance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        if name.lexeme in self.klass.methods:
            method = self.klass.methods[name.lexeme]
            return BoundMethod(self, method)
        raise LoxRuntimeError(f"Undefined property '{name.lexeme}'.", name)

    def __repr__(self):
        return f"<{self.klass.name} instance>"

class Function:
    def __init__(self, declaration: FunctionStmt):
        self.declaration = declaration

    def call(self, interpreter, arguments):
        return None

class BoundMethod:
    def __init__(self, instance, function):
        self.instance = instance
        self.function = function

    def call(self, interpreter, arguments):
        return self.function.call(interpreter, arguments)

    def __repr__(self):
        return f"<bound method {self.function.declaration.name.lexeme}>"

@exec.register
def _(stmt: ClassStmt, env: Env) -> None:
    klass = Class(stmt.name.lexeme)
    for method in stmt.methods:
        function = Function(method)
        klass.methods[method.name.lexeme] = function
    env[stmt.name.lexeme] = klass

@eval.register
def _(expr: Get, env: Env):
    obj = eval(expr.object, env)
    if isinstance(obj, Instance):
        return obj.get(expr.name)
    raise LoxRuntimeError(f"Only instances have properties.", expr.name)

class Function:
    def __init__(self, declaration: FunctionStmt):
        self.declaration = declaration

    def call(self, interpreter, arguments):
        local_env = env.Env()
        for param, arg in zip(self.declaration.params, arguments):
            local_env[param.lexeme] = arg
        for statement in self.declaration.body:
            exec(statement, local_env)
        return None

    def arity(self):
        return len(self.declaration.params)

    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"

@exec.register
def _(stmt: FunctionStmt, env: Env) -> None:
    function = Function(stmt)
    env[stmt.name.lexeme] = function
