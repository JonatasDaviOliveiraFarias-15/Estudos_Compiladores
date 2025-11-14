from dataclasses import dataclass, field
from typing import Any
from .tokens import Token, TokenType as TT

@dataclass
class Scanner:
    source: str
    start: int=0
    current: int=0
    line: int=1
    tokens: list[Token] = field(default_factory=list)

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start=self.current
            self.scan_token()
        self.tokens.append(Token(TT.EOF, "", None, self.line))
        return self.tokens
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.source)
    
    def scan_token(self):
        match self.advance():
            case "(":
                self.add_token(TT.LEFT_PAREN)
            case ")":
                self.add_token(TT.RIGHT_PAREN)
            case "{":
                self.add_token(TT.LEFT_BRACE)
            case "}":
                self.add_token(TT.RIGHT_BRACE)
            case ",":
                self.add_token(TT.COMMA)
            case ".":
                self.add_token(TT.DOT)
            case "-":
                self.add_token(TT.MINUS)
            case "+":
                self.add_token(TT.PLUS)
            case ";":
                self.add_token(TT.SEMICOLON)
            case "*":
                self.add_token(TT.STAR)
            case "_":
                self.add_token(TT.INVALID)
            case "!" if self.match("="):
                self.add_token(TT.BANG_EQUAL)
            case "!":
                self.add_token(TT.BANG)
            case "=" if self.match("="):
                self.add_token(TT.EQUAL_EQUAL)
            case "=":
                self.add_token(TT.EQUAL)
            case "<" if self.match("="):
                self.add_token(TT.LESS_EQUAL)
            case "<":
                self.add_token(TT.LESS)
            case ">" if self.match("="):
                self.add_token(TT.GREATER_EQUAL)
            case ">":
                self.add_token(TT.GREATER)
            case "/" if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            case "/":
                self.add_token(TT.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"' :
                self.string()
            case "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
                self.number()
            case c if is_alpha(c):
                self.identifier()

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()
        if self.is_at_end():
            print(f"[line {self.line}] Error: Unterminated string.")
            return
        self.advance()
        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TT.STRING, value)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        return char
    
    def add_token(self, type: TT, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return ""
        return self.source[self.current]
    
    def number(self):
        while is_digit(self.peek()):
            self.advance()
        if self.peek() == "." and is_digit(self.peek_next()):
            self.advance()
        while is_digit(self.peek()):
            self.advance()
        substring = self.source[self.start:self.current]
        self.add_token(TT.NUMBER, float(substring))

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]
    
    def identifier(self):
        while is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source[self.start: self.current]
        kind = KEYWORDS.get(text, TT.IDENTIFIER)
        self.add_token(kind)

def tokenize(source: str) -> list[Token]:
    scanner = Scanner(source)
    return scanner.scan_tokens()

def is_digit(char: str) -> bool:
    return char.isdigit() and char.isascii()

def is_alpha(char: str) -> bool:
    return char == "_" or (char.isalpha() and char.isascii())

def is_alpha_numeric(char: str) -> bool:
    return is_alpha(char) or is_digit(char)

KEYWORDS = {
        "and": TT.AND,
        "class": TT.CLASS,
        "else": TT.ELSE,
        "false": TT.FALSE,
        "for": TT.FOR,
        "fun": TT.FUN,
        "if": TT.IF,
        "nil": TT.NIL,
        "or": TT.OR,
        "print": TT.PRINT,
        "return": TT.RETURN,
        "super": TT.SUPER,
        "this": TT.THIS,
        "true": TT.TRUE,
        "var": TT.VAR,
        "while": TT.WHILE,
    }