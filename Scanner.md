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
