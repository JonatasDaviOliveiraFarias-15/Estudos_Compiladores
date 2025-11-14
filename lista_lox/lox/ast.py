from dataclasses import dataclass
from typing import Any
from .tokens import Token

class Expr:
    """Abstract Base Class for expressions"""

class Stmt:
    """Abstract Base Class for statements"""

@dataclass
class Expression(Stmt):
    expression: Expr

@dataclass
class Print(Stmt):
    expression: Expr

@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass
class Grouping(Expr):
    expression: Expr

@dataclass
class Literal(Expr):
    value: Any

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

@dataclass
class Program(Stmt):
    statements: list[Stmt]

@dataclass
class Var(Stmt):
    name: Token
    initializer: Expr

@dataclass
class Variable(Expr):
    name: Token 

@dataclass
class Assign(Expr):
    name: Token
    value: Expr

@dataclass
class Block(Stmt):
    statements: list[Stmt]

@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None

@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

@dataclass
class ClassStmt(Stmt):
    def __init__(self, name: Token, methods: list[Stmt]):
        self.name = name
        self.methods = methods

@dataclass
class FunctionStmt(Stmt):
    name: Token
    parameters: list[Token]
    body: list[Stmt]


@dataclass
class MethodCall(Expr):
    object: Expr 
    method: Token  

@dataclass
class Get(Expr):
    object: Expr
    name: Token

@dataclass
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

@dataclass
class MethodReference(Expr):
    object_expr: Expr 
    method_name: Token 

@dataclass
class FunctionStmt(Stmt):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body