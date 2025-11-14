from dataclasses import dataclass
from xml.etree.ElementTree import ParseError
from lox.environment_types import Env
from .tokens import Token
from lox.tokens import TokenType
from lox.errors import LoxSyntaxError
from dataclasses import field
from lox.ast import Stmt
from lox.errors import LoxStaticError
from lox.ast import *

@dataclass
class Parser:
    tokens: list[Token]
    current: int = 0

    def expression(self) -> Expr:
        return self.assignment()
    
    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    @staticmethod
    def _token_name(tok_type):
        if isinstance(tok_type, str):
            return tok_type
        return getattr(tok_type, "name", str(tok_type))

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end():
            return False
        expected_name = self._token_name(type_)
        actual = self.peek().type
        actual_name = actual if isinstance(actual, str) else getattr(actual, "name", str(actual))
        return actual_name == expected_name

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        t = self.peek().type
        tname = t if isinstance(t, str) else getattr(t, "name", str(t))
        return tname == "EOF"
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def comparison(self) -> Expr:
        expr = self.term()
        while self.match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr
    
    def term(self) -> Expr:
        expr = self.factor()
        while self.match("MINUS", "PLUS"):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr:
        expr = self.unary()
        while self.match("SLASH", "STAR"):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    
    def unary(self) -> Expr:
        if self.match("BANG", "MINUS"):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()

    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match("LEFT_PAREN"):
                expr = self.finish_call(expr)
            elif self.match("DOT"):
                name = self.consume("IDENTIFIER", "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check("RIGHT_PAREN"):
            while True:
                arguments.append(self.expression())
                if not self.match("COMMA"):
                    break
        paren = self.consume("RIGHT_PAREN", "Expect ')' after arguments.")
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        if self.match("FALSE"):
            return Literal(False)
        if self.match("TRUE"):
            return Literal(True)
        if self.match("NIL"):
            return Literal(None)
        if self.match("NUMBER", "STRING"):
            return Literal(self.previous().literal)
        if self.match("LEFT_PAREN"):
            expr = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return Grouping(expr)
        if self.match("IDENTIFIER"):
            return Variable(self.previous())
        raise self.error(self.peek(), "Expect expression.")

    def error(self, token: Token, message: str):
        if token.type == "EOF":
            where = "at end"
        else:
            where = f"at '{token.lexeme}'"
        full_message = f"[line {token.line}] Error {where}: {message}"
        error = LoxSyntaxError(full_message, token)
        self.errors.append(error)
        return error

    def synchronize(self):
        self.advance()
        boundary_tokens = {"CLASS", "FUN", "VAR", "FOR", "IF", "WHILE", "PRINT", "RETURN"}
        while not self.is_at_end():
            if self.previous().type == "SEMICOLON":
                return
            if self.peek().type in boundary_tokens:
                return
            self.advance()

    def __post_init__(self):
        self.errors: list[LoxSyntaxError] = []  
        for token in self.tokens:
            if token.type == "INVALID":
                self.error(token, "Unexpected character.")
        self.tokens = [t for t in self.tokens if t.type != "INVALID"]

    def statement(self) -> Stmt:
        match self.peek().type:
            case "PRINT":
                return self.print_statement()
            case "LEFT_BRACE":
                return self.block_statement()
            case "IF":
                return self.if_statement()
            case "WHILE":
                return self.while_statement()
            case "FOR":
                return self.for_statement()
            case _:
                return self.expression_statement()
            
    def print_statement(self) -> Print:
        self.consume("PRINT", "Expect 'print' keyword.")
        value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return Print(value)
    
    def expression_statement(self) -> Expression:
        expr = self.expression()
        self.consume("SEMICOLON", "Expect ';' after expression.")
        return Expression(expr)

    def function(self, kind):
        name = self.consume("IDENTIFIER", f"Expect {kind} name.")
        self.consume("LEFT_PAREN", f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check("RIGHT_PAREN"):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                parameters.append(self.consume("IDENTIFIER", "Expect parameter name."))
                if not self.match("COMMA"):
                    break
        self.consume("RIGHT_PAREN", "Expect ')' after parameters.")
        body = self.block_statement()  
        return FunctionStmt(name, parameters, body.statements)

    def var_declaration(self):
        name = self.consume("IDENTIFIER", "Expect variable name.")
        initializer = None
        if self.match("EQUAL"):
            initializer = self.expression()
        self.consume("SEMICOLON", "Expect ';' after variable declaration.")
        return Var(name, initializer)

    def assignment(self):
        expr = self.logic_or()
        if self.match("EQUAL"):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def block_statement(self) -> Block:
        self.consume("LEFT_BRACE", "Expect '{' to open block.")
        statements: list[Stmt] = []
        while not self.check("RIGHT_BRACE") and not self.is_at_end():
            statements.append(self.declaration())
        self.consume("RIGHT_BRACE", "Expect '}' after block.")
        return Block(statements)
        
    def if_statement(self) -> If:
        self.consume("IF", "Expect 'if'.")
        self.consume("LEFT_PAREN", "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.statement()
        return If(condition, then_branch, else_branch)

    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while self.match("OR"):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)
        return expr

    def logic_and(self) -> Expr:
        expr = self.equality()
        while self.match("AND"):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr

    def while_statement(self) -> While:
        self.consume("WHILE", "Expect 'while'.")
        self.consume("LEFT_PAREN", "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after condition.")
        body = self.statement()
        return While(condition, body)

    def for_statement(self):
        self.consume("FOR", "Expect 'for'.")
        self.consume("LEFT_PAREN", "Expect '(' after 'for'.")
        initializer = None
        if self.match("SEMICOLON"):
            initializer = None
        elif self.match("VAR"):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check("SEMICOLON"):
            condition = self.expression()
        self.consume("SEMICOLON", "Expect ';' after loop condition.")
        increment = None
        if not self.check("RIGHT_PAREN"):
            increment = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after for clauses.")
        body = self.statement()
        if increment is not None:
            body = Block([body, Expression(increment)])
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])
        return body

    def declaration(self) -> Stmt:
        if self.match(TokenType.CLASS):
            return self.class_declaration()
        if self.match(TokenType.FUN):
            return self.function("function")
        if self.match(TokenType.VAR):
            return self.var_declaration()
        return self.statement()

    def class_declaration(self) -> ClassStmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function_declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return ClassStmt(name, methods)

    def function_declaration(self) -> FunctionStmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")
        body: list[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                body.append(stmt)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after function body.")
        return FunctionStmt(name, parameters, body)

def parse(tokens: list[Token]) -> Stmt:
    parser = Parser(tokens)
    statements = []
    while not parser.is_at_end():
        try:
            stmt = parser.declaration()
            if stmt is not None:
                statements.append(stmt)
        except LoxSyntaxError:
            parser.synchronize()
    if parser.errors:
        raise LoxStaticError(parser.errors)
    return Program(statements)

def run(tokens):
    program = parse(tokens)
    exec(program, Env())