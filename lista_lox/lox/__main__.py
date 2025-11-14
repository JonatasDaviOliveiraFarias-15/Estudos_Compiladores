from lox.scanner import tokenize
from lox.parser import parse
from lox.interpreter import exec as interpreter_exec, Env
from lox.errors import LoxRuntimeError, LoxStaticError
from lox.ast import Program 

class Lox:
    def __init__(self):
        self.env = Env()

    def run(self, source: str) -> str:
        try:
            tokens = tokenize(source)
            statements = parse(tokens)  
            interpreter_exec(statements, self.env)
            return ""  
        except LoxRuntimeError as e:
            print(f"runtime error: {e}")
            return f"runtime error: {e}"
        except LoxStaticError as e:
            for error in e.errors:
                print(error)
            return "\n".join(str(err) for err in e.errors)