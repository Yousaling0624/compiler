from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    VOID = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    SCANF = auto()
    PRINTF = auto()

    # Identifiers and literals
    ID = auto()
    INT_LIT = auto()
    FLOAT_LIT = auto()
    CHAR_LIT = auto()
    STRING_LIT = auto()

    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    STAR = auto()        # *
    SLASH = auto()       # /
    PERCENT = auto()     # %
    ASSIGN = auto()      # =
    EQ = auto()          # ==
    NE = auto()          # !=
    LT = auto()          # <
    GT = auto()          # >
    LE = auto()          # <=
    GE = auto()          # >=
    AND = auto()         # &&
    OR = auto()          # ||
    NOT = auto()         # !
    AMPERSAND = auto()   # &

    # Delimiters
    LPAREN = auto()      # (
    RPAREN = auto()      # )
    LBRACE = auto()      # {
    RBRACE = auto()      # }
    SEMICOLON = auto()   # ;
    COMMA = auto()       # ,
    DOT = auto()         # .
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]

    EOF = auto()


KEYWORDS = {
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "char": TokenType.CHAR,
    "void": TokenType.VOID,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "return": TokenType.RETURN,
    "scanf": TokenType.SCANF,
    "printf": TokenType.PRINTF,
}


class Token:
    def __init__(self, token_type, value, line, col):
        self.type = token_type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line}:{self.col})"
