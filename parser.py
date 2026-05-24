from tokens import TokenType
from ast_nodes import (
    Program, FuncDef, Block, VarDecl, Assign, BinaryOp, UnaryOp,
    Identifier, IntegerLit, FloatLit, CharLit, StringLit,
    IfStmt, WhileStmt, ForStmt, CallStmt, ReturnStmt, EmptyStmt,
    MemberAccess, ArrayAccess
)


class ParserError(Exception):
    def __init__(self, msg, token):
        loc = f"L{token.line}:{token.col}" if token else "EOF"
        super().__init__(f"Parser error at {loc}: {msg}")
        self.token = token


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]

    def expect(self, token_type):
        if self.current.type == token_type:
            tok = self.current
            self.advance()
            return tok
        raise ParserError(f"Expected {token_type}, got {self.current.type}", self.current)

    def match(self, token_type):
        if self.current.type == token_type:
            self.advance()
            return True
        return False

    # -------- Program --------

    def parse_program(self):
        functions = []
        while self.current.type != TokenType.EOF:
            functions.append(self.parse_func_def())
        return Program(functions)

    # -------- Function Definition --------

    def parse_func_def(self):
        return_type = self.parse_type()
        name = self.expect(TokenType.ID).value
        self.expect(TokenType.LPAREN)
        params = self.parse_params()
        self.expect(TokenType.RPAREN)
        body = self.parse_block()
        return FuncDef(return_type, name, params, body)

    def parse_params(self):
        params = []
        if self.current.type in (TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
            ptype = self.parse_type()
            pname = self.expect(TokenType.ID).value
            params.append((ptype, pname))
            while self.match(TokenType.COMMA):
                ptype = self.parse_type()
                pname = self.expect(TokenType.ID).value
                params.append((ptype, pname))
        return params

    def parse_type(self):
        if self.match(TokenType.INT):
            return "int"
        elif self.match(TokenType.FLOAT):
            return "float"
        elif self.match(TokenType.CHAR):
            return "char"
        elif self.match(TokenType.VOID):
            return "void"
        raise ParserError(f"Expected type, got {self.current.type}", self.current)

    # -------- Block & Statements --------

    def parse_block(self):
        self.expect(TokenType.LBRACE)
        stmts = []
        while self.current.type not in (TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.parse_block_item())
        self.expect(TokenType.RBRACE)
        return Block(stmts)

    def parse_block_item(self):
        if self.current.type in (TokenType.INT, TokenType.FLOAT, TokenType.CHAR):
            return self.parse_var_decl()
        return self.parse_statement()

    def parse_var_decl(self):
        var_type = self.parse_type()
        name = self.expect(TokenType.ID).value
        # Array declaration: name[size]
        array_size = None
        if self.match(TokenType.LBRACKET):
            array_size = self.expect(TokenType.INT_LIT).value
            self.expect(TokenType.RBRACKET)
        init = None
        if self.match(TokenType.ASSIGN):
            init = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return VarDecl(var_type, name, init)

    def parse_statement(self):
        if self.match(TokenType.LBRACE):
            stmts = []
            while self.current.type not in (TokenType.RBRACE, TokenType.EOF):
                stmts.append(self.parse_block_item())
            self.expect(TokenType.RBRACE)
            return Block(stmts)
        elif self.match(TokenType.IF):
            return self.parse_if_stmt()
        elif self.match(TokenType.WHILE):
            return self.parse_while_stmt()
        elif self.match(TokenType.FOR):
            return self.parse_for_stmt()
        elif self.match(TokenType.RETURN):
            return self.parse_return_stmt()
        elif self.match(TokenType.PRINTF):
            return self.parse_printf_stmt()
        elif self.match(TokenType.SCANF):
            return self.parse_scanf_stmt()
        elif self.match(TokenType.SEMICOLON):
            return EmptyStmt()
        else:
            return self.parse_expr_stmt()

    def parse_expr_stmt(self):
        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return expr

    # -------- If / While / For --------

    def parse_if_stmt(self):
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        then_stmt = self.parse_statement()
        else_stmt = None
        if self.match(TokenType.ELSE):
            else_stmt = self.parse_statement()
        return IfStmt(condition, then_stmt, else_stmt)

    def parse_while_stmt(self):
        self.expect(TokenType.LPAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        return WhileStmt(condition, body)

    def parse_for_stmt(self):
        self.expect(TokenType.LPAREN)
        init = self.parse_expression() if self.current.type != TokenType.SEMICOLON else None
        self.expect(TokenType.SEMICOLON)
        condition = self.parse_expression() if self.current.type != TokenType.SEMICOLON else None
        self.expect(TokenType.SEMICOLON)
        update = self.parse_expression() if self.current.type != TokenType.RPAREN else None
        self.expect(TokenType.RPAREN)
        body = self.parse_statement()
        return ForStmt(init, condition, update, body)

    # -------- Return --------

    def parse_return_stmt(self):
        expr = None
        if self.current.type != TokenType.SEMICOLON:
            expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ReturnStmt(expr)

    # -------- Printf / Scanf --------

    def parse_printf_stmt(self):
        self.expect(TokenType.LPAREN)
        fmt = self.expect(TokenType.STRING_LIT)
        args = []
        while self.match(TokenType.COMMA):
            args.append(self.parse_expression())
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return CallStmt("printf", [StringLit(fmt.value)] + args)

    def parse_scanf_stmt(self):
        self.expect(TokenType.LPAREN)
        fmt = self.expect(TokenType.STRING_LIT)
        args = []
        while self.match(TokenType.COMMA):
            self.expect(TokenType.AMPERSAND)
            ident = self.expect(TokenType.ID)
            args.append(Identifier(ident.value))
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return CallStmt("scanf", [StringLit(fmt.value)] + args)

    # -------- Expressions (precedence climbing) --------

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()
        if self.match(TokenType.ASSIGN):
            right = self.parse_assignment()
            return Assign(left, right)
        return left

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.match(TokenType.OR):
            right = self.parse_logical_and()
            left = BinaryOp(left, '||', right)
        return left

    def parse_logical_and(self):
        left = self.parse_equality()
        while self.match(TokenType.AND):
            right = self.parse_equality()
            left = BinaryOp(left, '&&', right)
        return left

    def parse_equality(self):
        left = self.parse_relational()
        while self.current.type in (TokenType.EQ, TokenType.NE):
            op = self.current.value
            self.advance()
            right = self.parse_relational()
            left = BinaryOp(left, op, right)
        return left

    def parse_relational(self):
        left = self.parse_additive()
        while self.current.type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op = self.current.value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current.value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current.type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.current.value
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        return left

    def parse_unary(self):
        if self.match(TokenType.MINUS):
            operand = self.parse_unary()
            return UnaryOp('-', operand)
        elif self.match(TokenType.NOT):
            operand = self.parse_unary()
            return UnaryOp('!', operand)
        return self.parse_primary()

    def parse_primary(self):
        node = None
        if self.match(TokenType.INT_LIT):
            node = IntegerLit(self.tokens[self.pos - 1].value)
        elif self.match(TokenType.FLOAT_LIT):
            node = FloatLit(self.tokens[self.pos - 1].value)
        elif self.match(TokenType.CHAR_LIT):
            node = CharLit(self.tokens[self.pos - 1].value)
        elif self.match(TokenType.STRING_LIT):
            node = StringLit(self.tokens[self.pos - 1].value)
        elif self.match(TokenType.LPAREN):
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
        elif self.current.type == TokenType.ID:
            name = self.current.value
            self.advance()
            # Function call
            if self.match(TokenType.LPAREN):
                args = self.parse_args()
                self.expect(TokenType.RPAREN)
                node = CallStmt(name, args)
            else:
                node = Identifier(name)
        else:
            raise ParserError(f"Unexpected token in expression: {self.current.type}", self.current)

        # Postfix operations: .member and [index]
        while node is not None:
            if self.match(TokenType.DOT):
                member = self.expect(TokenType.ID).value
                node = MemberAccess(node, member)
            elif self.match(TokenType.LBRACKET):
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                node = ArrayAccess(node, index)
            else:
                break
        return node

    def parse_args(self):
        args = []
        if self.current.type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                args.append(self.parse_expression())
        return args
