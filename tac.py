from enum import Enum, auto


class TACOp(Enum):
    ASSIGN = auto()        # dest = src1 op src2
    UNARY = auto()         # dest = op src
    COPY = auto()          # dest = src
    LABEL = auto()         # L:
    GOTO = auto()          # goto L
    IF_GOTO = auto()       # if cond goto L
    IF_FALSE_GOTO = auto() # ifFalse cond goto L
    PARAM = auto()         # param arg
    CALL = auto()          # dest = call func, nargs
    RETURN = auto()        # return val
    ADDR = auto()          # dest = &src


class TACInstr:
    def __init__(self, op, dest=None, src1=None, src2=None, op_str=None):
        self.op = op
        self.dest = dest      # result variable / label name
        self.src1 = src1      # operand 1
        self.src2 = src2      # operand 2 (for binary ops) or nargs (for CALL)
        self.op_str = op_str  # operator string for ASSIGN/UNARY

    def __repr__(self):
        if self.op == TACOp.ASSIGN:
            return f"{self.dest} = {self.src1} {self.op_str} {self.src2}"
        elif self.op == TACOp.UNARY:
            return f"{self.dest} = {self.op_str} {self.src1}"
        elif self.op == TACOp.COPY:
            return f"{self.dest} = {self.src1}"
        elif self.op == TACOp.LABEL:
            return f"{self.dest}:"
        elif self.op == TACOp.GOTO:
            return f"goto {self.dest}"
        elif self.op == TACOp.IF_GOTO:
            return f"if {self.src1} goto {self.dest}"
        elif self.op == TACOp.IF_FALSE_GOTO:
            return f"ifFalse {self.src1} goto {self.dest}"
        elif self.op == TACOp.PARAM:
            return f"param {self.src1}"
        elif self.op == TACOp.CALL:
            s = f"{self.dest} = " if self.dest else ""
            return f"{s}call {self.src1}, {self.src2}"
        elif self.op == TACOp.RETURN:
            return f"return {self.src1}" if self.src1 else "return"
        elif self.op == TACOp.ADDR:
            return f"{self.dest} = &{self.src1}"
        return str(self.op)
