# Prova 1 
Primeiramente temos que saber a diferença entre lexemas e tokens e é a maneira como iniciarei esse estudo.
## Lexemas e Tokens
Lexema e uma sequência de caracteres que um usuário escreveu no código dele, por exemplo na linguagem lox temos:

```print "Hello, world!";```

```print``` é um lexema

```Hello, world!``` é um lexema

```;``` é um lexema

Ou seja, lexemas são separações do código em estruturas menores.

Agora quanto aos tokens, são uma representação estruturada de um lexema, usando o print do exemplo anterior:

```Token(TokenType.PRINT, "print", None, 1)```

O token vai ter o tipo dele, nesse caso um print, vai ter o texto que foi escrito que nesse caso foi um print, vai ter o valor literal dele (basicamente para números floats por exemplo ele transforma em string para depois transformar em float, esse valor literal já é o valor em float) e por último tem a linha em que ele foi escrito.

## Scanner
Aqui farei a análise e simplificação de cada parte do código que forma o scanner do nosso compilador de lox. Inicialmente irei colocar o código completo e irei destrinchando ele por partes de maneira mais simplificada.

```
from dataclasses import dataclass, field
from typing import Any
from .tokens import Token, TokenType as TT

@dataclass
class Scanner:
    start: int=0
    current: int=0
    line: int=1
    source: str
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
            self.add_token(TT.INVALID)
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
        self.tokens.append(Token(type, text, self.line, literal))
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
```

### Importações

```
from dataclasses import dataclass, field
from typing import Any
from .tokens import Token, TokenType as TT
```

Básicamente o que estamos fazendo aqui é importando uma dataclass que é uma função que vai auxiliar a gente na criação da classe scanner, funciona meio como uma estrutura de dados. O field por exemplo vai garantir que cada vez que você instânciar um scanner ele tenha a própia lista de tokens.

O .tokens está chamando uma lista de tokens pré-estabelecidos que estão salvos em outros arquivos e que vai nos auxiliar, aqui está ela salvo no arquivo tokens na mesma pasta que o scanner:

```
from enum import IntEnum, auto

class TokenType(IntEnum):
    # Single-character tokens.
    LEFT_PAREN = auto(); RIGHT_PAREN = auto()
    LEFT_BRACE = auto(); RIGHT_BRACE = auto()
    COMMA = auto(); DOT = auto(); SEMICOLON = auto()
    MINUS = auto(); PLUS = auto(); SLASH = auto(); STAR = auto()

    # One or two character tokens.
    BANG = auto(); BANG_EQUAL = auto()
    EQUAL= auto(); EQUAL_EQUAL = auto()
    GREATER= auto(); GREATER_EQUAL = auto()
    LESS= auto(); LESS_EQUAL = auto()

    # Literals.
    IDENTIFIER = auto(); STRING = auto(); NUMBER = auto()

    # Keywords.
    AND = auto(); CLASS = auto(); ELSE = auto(); FALSE = auto()
    FUN = auto(); FOR = auto(); IF = auto(); NIL = auto()
    OR = auto(); PRINT = auto(); RETURN = auto(); SUPER = auto()
    THIS = auto(); TRUE = auto(); VAR = auto(); WHILE = auto()

    # Special tokens.
    EOF = auto()
    INVALID = auto()
    UNTERMINATED_STRING = auto()


from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    type: TokenType
    lexeme: str
    line: int
    literal: Any = None

    def __str__(self):
        return f"{self.type.name} {self.lexeme} {self.literal}"
```

O que você precisa saber desse código acima é que ele vai te auxiliar na hora de criar o scanner na parte de tokens, fora isso não tenha medo de copiar e colocar para um arquivo dentro da mesma pasta do seu projeto.

### Classe scanner

Vamos por partes na análise da classe scanner começando com os parâmetros iniciais.

```
@dataclass
class Scanner:
    start: int=0
    current: int=0
    line: int=1
    source: str
    tokens: list[Token] = field(default_factory=list)
```

Aqui a gente começa usando o ```@dataclass``` para nos auxiliar como já foi falado anteriormente.

```start```: marca o início do lexema atual.

```current```: posição atual que está sendo lida da string ```source```.

```line```: indica a linha que está sendo lida (para indicar possíveis erros por exemplo).

```source```: é o código inteiro digitado pelo usuário em forma de string.

```tokens```: é a lista final de todos os tokens que foram gerados pela leitura do scanner.

Agora vamos adentrar dentro das funções que se encontram dentro da class scanner:

### Método Principal

```
def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start=self.current
            self.scan_token()
        self.tokens.append(Token(TT.EOF, "", None, self.line))
        return self.tokens
```

Aqui ele vai fazer o scan de tokens, enquanto não for o fim do código ele continua lendo, quando acabar ele adiciona um tokens especial de EOF (end of file/final de arquivo). Após isso ele vai retornar toda a lista de tokens que foi gerada. Para análisar os tokens ele usa o função ```scan_token()``` que veremos adiante.

### Controle do Fim

```
def is_at_end(self) -> bool:
    return self.current >= len(self.source)
```

Essa função vai controlar se o código chegou ao fim, básicamente se o ```current``` for maior ou igual ao tamanho do código, ele retorna ```True```, ou seja, ele chegou ao fim da leitura do código.

### Leitura de um Token

```
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
```
