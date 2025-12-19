# parser.py
"""
my language use simple grammar:

program ::= (decl | expr)*
decl ::= IDENT ':=' expr
expr ::= atom+
atom ::= LITERAL
       | IDENT
       | quot
       | list
quot ::= '[' expr ']'
list ::= '{' expr '}'
"""
from interpreter.lexer import TokenType


class ASTNode:
    def accept(self, visitor):
        method_name = f'visit_{self.__class__.__name__.lower()}'
        # print(f'Visiting {method_name}')
        visit_method = getattr(visitor, method_name, visitor.generic_visit)
        return visit_method(self)


class Program(ASTNode):
    def __init__(self):
        self.statements = []

    def add_statement(self, stmt):
        self.statements.append(stmt)

    def __repr__(self):
        return f'Program({self.statements})'


class Expr(ASTNode):
    def __init__(self):
        self.atoms = []

    def add_atom(self, atom):
        self.atoms.append(atom)

    def __repr__(self):
        return f'Expr({self.atoms})'


class Decl(ASTNode):
    def __init__(self, word, expr):
        self.word = word
        self.expr = expr

    def __repr__(self):
        return f'Decl({self.word}, {self.expr})'


class Literal(ASTNode):
    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return f'Literal({self.content})'


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Identifier({self.name})'


class List(ASTNode):
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return f'List({self.items})'


class Quot(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f'Quot({self.expr})'



class ParserError(Exception):
    pass


def is_match(left, right):
    table = {'(': ')', '[': ']', '{': '}'}
    return table.get(left, 0) == right


class Parser:
    def __init__(self):
        self.tokens = []
        self.index = 0

    def error(self, message):
        raise ParserError(message)

    def advance(self):
        self.index += 1

    def peek(self):
        if self.index >= len(self.tokens):
            raise ParserError('Unexpected EOF')
        return self.tokens[self.index]

    def peek_next(self):
        if self.index + 1 >= len(self.tokens):
            raise ParserError('Unexpected EOF')
        return self.tokens[self.index + 1]

    def eof(self):
        return self.index == len(self.tokens)

    def expect(self, _type: TokenType):
        current = self.peek()
        if current.type != _type:
            raise ParserError(f"Expected {_type} but got {current.type}")
        return current

    def consume(self, _type: TokenType):
        current = self.peek()
        if current.type != _type:
            raise ParserError(f"Expected {_type} but got {current.type}")
        self.advance()
        return current

    def parse(self, tokens: list) -> Program:
        self.tokens = tokens
        self.index = 0
        result = self._parse_program()
        return result

    def _parse_program(self):
        program = Program()
        while not self.eof():
            if self._is_declaration():
                line = self._parse_declaration()
            else:
                line = self._parse_expression()
            program.add_statement(line)
        return program

    def _parse_declaration(self):
        name_token = self.consume(TokenType.IDENTIFIER)
        word = Identifier(name_token.value)
        self.consume(TokenType.ASSIGNMENT)
        expr = self._parse_expression()
        return Decl(word, expr)

    def _parse_expression(self):
        expr = Expr()
        while not self.eof() and self.peek().type != TokenType.NEWLINE and self.peek().type != TokenType.PARENTHESIS_R:
            atom = self._parse_atom()
            expr.add_atom(atom)
        return expr

    def _parse_atom(self):
        current = self.peek()
        if current.type == TokenType.LITERAL:
            self.consume(TokenType.LITERAL)
            return Literal(current.value)

        if current.type == TokenType.IDENTIFIER:
            self.consume(TokenType.IDENTIFIER)
            return Identifier(current.value)

        if current.type == TokenType.PARENTHESIS_L:
            left = current.value
            self.consume(TokenType.PARENTHESIS_L)
            expr = self._parse_expression()
            right = self.consume(TokenType.PARENTHESIS_R).value
            if not is_match(left, right):
                raise ParserError(f"Unmatched parentheses: {left} and {right}")
            if left == '[':
                return Quot(expr)
            if left == '{':
                return List(expr)
            raise ParserError(f"Unimplemented parentheses: {left + right}")

        raise ParserError(f"Unexpected token: {current}")


    def _is_declaration(self):
        if self.index + 1 >= len(self.tokens):
            return False
        second = self.peek_next()
        return second.type == TokenType.ASSIGNMENT




if __name__ == '__main__':
    from interpreter.lexer import *
    lexer = Lexer()
    parser = Parser()
    source = input("Please enter a source code: ")
    tokens = lexer.parse(source)
    result = parser.parse(tokens)
    print(result)
