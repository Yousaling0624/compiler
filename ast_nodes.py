class ASTNode:
    """Base class for all AST nodes."""
    pass


class Program(ASTNode):
    def __init__(self, functions):
        self.functions = functions  # list of FuncDef

    def __repr__(self):
        return f"Program({self.functions})"


class FuncDef(ASTNode):
    def __init__(self, return_type, name, params, body):
        self.return_type = return_type  # str: "int", "float", "char", "void"
        self.name = name                # str
        self.params = params            # list of (type_str, name_str)
        self.body = body                # Block

    def __repr__(self):
        return f"FuncDef({self.return_type}, {self.name}, {self.params})"


class Block(ASTNode):
    def __init__(self, stmts):
        self.stmts = stmts  # list of statements / declarations

    def __repr__(self):
        return f"Block({self.stmts})"


class VarDecl(ASTNode):
    def __init__(self, var_type, name, init=None):
        self.var_type = var_type  # str
        self.name = name          # str
        self.init = init          # Expr or None

    def __repr__(self):
        return f"VarDecl({self.var_type}, {self.name}, init={self.init})"


class Assign(ASTNode):
    def __init__(self, left, right):
        self.left = left    # Identifier (or lvalue)
        self.right = right  # Expr

    def __repr__(self):
        return f"Assign({self.left}, {self.right})"


class BinaryOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left    # Expr
        self.op = op        # str: + - * / % == != < > <= >= && ||
        self.right = right  # Expr

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op}, {self.right})"


class UnaryOp(ASTNode):
    def __init__(self, op, operand):
        self.op = op          # str: - ! (negate, logical not)
        self.operand = operand  # Expr

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.operand})"


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"ID({self.name})"


class IntegerLit(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Int({self.value})"


class FloatLit(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"


class CharLit(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Char({self.value!r})"


class StringLit(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Str({self.value!r})"


class IfStmt(ASTNode):
    def __init__(self, condition, then_stmt, else_stmt=None):
        self.condition = condition
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def __repr__(self):
        return f"If({self.condition}, {self.then_stmt}, else={self.else_stmt})"


class WhileStmt(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition}, {self.body})"


class ForStmt(ASTNode):
    def __init__(self, init, condition, update, body):
        self.init = init          # Expr or None
        self.condition = condition  # Expr or None
        self.update = update      # Expr or None
        self.body = body          # Statement

    def __repr__(self):
        return f"For({self.init}; {self.condition}; {self.update}) {self.body}"


class CallStmt(ASTNode):
    def __init__(self, name, args):
        self.name = name  # str: "printf" or "scanf"
        self.args = args  # list of Expr

    def __repr__(self):
        return f"Call({self.name}, {self.args})"


class ReturnStmt(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr  # Expr or None

    def __repr__(self):
        return f"Return({self.expr})"


class EmptyStmt(ASTNode):
    def __repr__(self):
        return "Empty"


class MemberAccess(ASTNode):
    """Access a struct member: object.member"""
    def __init__(self, object, member):
        self.object = object    # Expression (the struct)
        self.member = member    # str (member name)

    def __repr__(self):
        return f"MemberAccess({self.object}, {self.member})"


class ArrayAccess(ASTNode):
    """Access array element: array[index]"""
    def __init__(self, array, index):
        self.array = array    # Expression (the array)
        self.index = index    # Expression (the index)

    def __repr__(self):
        return f"ArrayAccess({self.array}, {self.index})"
