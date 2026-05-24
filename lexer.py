from tokens import Token, TokenType, KEYWORDS


class LexerError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"Lexer error at L{line}:{col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.current_char = source[0] if source else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1
        self.current_char = self.source[self.pos] if self.pos < len(self.source) else None

    def peek(self):
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t\n\r':
            self.advance()

    def skip_comment(self):
        if self.current_char == '/' and self.peek() == '/':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
        elif self.current_char == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            while self.current_char is not None:
                if self.current_char == '*' and self.peek() == '/':
                    self.advance()
                    self.advance()
                    break
                self.advance()

    def skip_whitespace_and_comments(self):
        while self.current_char is not None:
            if self.current_char in ' \t\n\r':
                self.skip_whitespace()
            elif self.current_char == '/' and self.peek() in ('/', '*'):
                self.skip_comment()
            else:
                break

    def read_identifier_or_keyword(self):
        start_col = self.col
        start_line = self.line
        chars = []
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            chars.append(self.current_char)
            self.advance()
        lexeme = ''.join(chars)
        token_type = KEYWORDS.get(lexeme, TokenType.ID)
        return Token(token_type, lexeme, start_line, start_col)

    def read_number(self):
        start_col = self.col
        start_line = self.line
        chars = []
        is_float = False
        while self.current_char is not None and self.current_char.isdigit():
            chars.append(self.current_char)
            self.advance()
        if self.current_char == '.' and self.peek() and self.peek().isdigit():
            is_float = True
            chars.append(self.current_char)
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                chars.append(self.current_char)
                self.advance()
        lexeme = ''.join(chars)
        if is_float:
            return Token(TokenType.FLOAT_LIT, float(lexeme), start_line, start_col)
        return Token(TokenType.INT_LIT, int(lexeme), start_line, start_col)

    def read_char_literal(self):
        start_col = self.col
        start_line = self.line
        self.advance()  # skip opening '
        ch = self.current_char
        if ch == '\\':
            self.advance()
            escape = self.current_char
            escape_map = {'n': '\n', 't': '\t', '\\': '\\', "'": "'", '"': '"', '0': '\0'}
            ch = escape_map.get(escape, escape)
        self.advance()
        if self.current_char == "'":
            self.advance()
        return Token(TokenType.CHAR_LIT, ch, start_line, start_col)

    def read_string_literal(self):
        start_col = self.col
        start_line = self.line
        self.advance()  # skip opening "
        chars = []
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                escape = self.current_char
                escape_map = {'n': '\n', 't': '\t', '\\': '\\', '"': '"', '0': '\0'}
                chars.append(escape_map.get(escape, escape))
            else:
                chars.append(self.current_char)
            self.advance()
        if self.current_char == '"':
            self.advance()
        return Token(TokenType.STRING_LIT, ''.join(chars), start_line, start_col)

    def get_next_token(self):
        self.skip_whitespace_and_comments()

        if self.current_char is None:
            return Token(TokenType.EOF, None, self.line, self.col)

        ch = self.current_char
        line, col = self.line, self.col

        # Identifiers and keywords
        if ch.isalpha() or ch == '_':
            return self.read_identifier_or_keyword()

        # Numbers
        if ch.isdigit():
            return self.read_number()

        # Character literal
        if ch == "'":
            return self.read_char_literal()

        # String literal
        if ch == '"':
            return self.read_string_literal()

        # Multi-character operators
        if ch == '=' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.EQ, '==', line, col)
        if ch == '!' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.NE, '!=', line, col)
        if ch == '<' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.LE, '<=', line, col)
        if ch == '>' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.GE, '>=', line, col)
        if ch == '&' and self.peek() == '&':
            self.advance()
            self.advance()
            return Token(TokenType.AND, '&&', line, col)
        if ch == '|' and self.peek() == '|':
            self.advance()
            self.advance()
            return Token(TokenType.OR, '||', line, col)

        # Single-character operators and delimiters
        single_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '=': TokenType.ASSIGN,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '!': TokenType.NOT,
            '&': TokenType.AMPERSAND,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
        }
        if ch in single_map:
            self.advance()
            return Token(single_map[ch], ch, line, col)

        raise LexerError(f"Unexpected character: {ch!r}", line, col)

    def tokenize(self):
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
