from ast import *
from lox.interpreter import Env, is_truthy

@exec.register
def _(stmt: While, env: Env) -> None:
    while is_truthy(eval(stmt.condition, env)):
        exec(stmt.body, env)