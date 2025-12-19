# lexer.py
from enum import Enum


NON_IDENTIFIER_SYMBOLS = frozenset(" :()[]{}\"\'\n")
OPERATOR_SYMBOLS = frozenset("+-*/%=")

class TokenType(Enum):
    LITERAL = 1
    IDENTIFIER = 2
    NEWLINE = 3
    PARENTHESIS_L = 4
    PARENTHESIS_R = 5
    ASSIGNMENT = 6


class Token:
    def __init__(self, _type, value):
        self.type = _type
        self.value = value

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)})'


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self):
        self.source = ""
        self.pos = 0
        self.current_char = None

    def error(self, message):
        raise LexerError(f'Token error: {message}')

    def advance(self):
        self.pos += 1
        if self.pos >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.pos]

    def next_token(self):
        # skip spaces
        while self.current_char == ' ':
            self.advance()

        if self.current_char == '\n':
            token = Token(TokenType.NEWLINE, self.current_char)
            self.advance()
            return token

        if self.current_char in "([{":
            token = Token(TokenType.PARENTHESIS_L, self.current_char)
            self.advance()
            return token

        if self.current_char in ")]}":
            token = Token(TokenType.PARENTHESIS_R, self.current_char)
            self.advance()
            return token

        if self.current_char == ':':
            return self._get_assignment_token()
        
        if self.current_char.isdigit():
            return self._get_number_token()

        if self.current_char in "\'\"":
            return self._get_string_token()

        return self._get_identifier_token()

    def parse(self, source):
        self.source = source
        self.pos = 0
        self.current_char = self.source[self.pos]
        tokens = []
        while self.current_char:
            tokens.append(self.next_token())
        return tokens

    def consume(self, char):
        if self.current_char == char:
            self.advance()
            return
        else:
            if self.current_char is None:
                self.error(f'Unexpected EOF')
            self.error(f'Unexpected character "{self.current_char}"')

    def _get_number_token(self):
        res = ""
        while self.current_char and self.current_char.isdigit():
            res += self.current_char
            self.advance()

        if self.current_char != '.':
            return Token(TokenType.LITERAL, int(res))

        res += self.current_char
        self.advance()

        while self.current_char and self.current_char.isdigit():
            res += self.current_char
            self.advance()

        return Token(TokenType.LITERAL, float(res))

    def _get_string_token(self):
        res = ""
        quot = self.current_char  # 记录引号类型（单引号或双引号）
        self.advance()

        while self.current_char and self.current_char != quot:
            if self.current_char == '\n':
                self.error("Unexpected End of Line")

            # 处理转义字符
            if self.current_char == '\\':
                self.advance()  # 跳过反斜杠
                if not self.current_char:
                    break  # EOF检查

                # 处理常见转义序列
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    'b': '\b',
                    'f': '\f',
                    '\\': '\\',
                    '"': '"',
                    "'": "'",
                    # 可以添加更多转义序列
                }

                if self.current_char in escape_map:
                    res += escape_map[self.current_char]
                    self.advance()
                elif self.current_char == 'x':
                    # 处理十六进制转义：\xHH
                    self.advance()
                    hex_digits = self._read_hex_digits(2)
                    res += chr(int(hex_digits, 16))
                elif self.current_char == 'u':
                    # 处理Unicode转义：\uHHHH
                    self.advance()
                    hex_digits = self._read_hex_digits(4)
                    res += chr(int(hex_digits, 16))
                elif self.current_char == 'U':
                    # 处理长Unicode转义：\UHHHHHHHH
                    self.advance()
                    hex_digits = self._read_hex_digits(8)
                    res += chr(int(hex_digits, 16))
                else:
                    # 未知转义字符，保持原样（包括反斜杠）
                    res += '\\' + self.current_char
                    self.advance()
            else:
                res += self.current_char
                self.advance()

        # 消费结束引号
        self.consume(quot)
        return Token(TokenType.LITERAL, res)

    def _get_identifier_token(self):
        if self.current_char in OPERATOR_SYMBOLS:
            token = Token(TokenType.IDENTIFIER, self.current_char)
            self.advance()
            return token

        res = ""
        while (self.current_char and
               self.current_char not in NON_IDENTIFIER_SYMBOLS and
               self.current_char not in OPERATOR_SYMBOLS):
            res += self.current_char
            self.advance()
        return Token(TokenType.IDENTIFIER, res)

    def _read_hex_digits(self, count):
        """读取指定数量的十六进制数字"""
        digits = ""
        for _ in range(count):
            if self.current_char and self.current_char.upper() in "0123456789ABCDEF":
                digits += self.current_char
                self.advance()
            else:
                self.error(f"Expected {count} hex digits after escape sequence")
        return digits

    def _get_assignment_token(self):
        self.consume(':')
        try:
            self.consume('=')
            return Token(TokenType.ASSIGNMENT, ':=')
        except LexerError:
            return Token(TokenType.IDENTIFIER, ':')


if __name__ == '__main__':
    source = input('Please enter a source code: ')
    lexer = Lexer()
    tokens = lexer.parse(source)
    print(tokens)