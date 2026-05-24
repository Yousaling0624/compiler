"""Annotated syntax tree printer — for course design Task 2."""

from ast_nodes import (
    Program, FuncDef, Block, VarDecl, Assign, BinaryOp, UnaryOp,
    Identifier, IntegerLit, FloatLit, CharLit, StringLit,
    IfStmt, WhileStmt, ForStmt, CallStmt, ReturnStmt, EmptyStmt,
    MemberAccess, ArrayAccess
)


def print_annotated_tree(node, indent=0):
    prefix = "  " * indent
    child_prefix = "  " * (indent + 1)

    if isinstance(node, Program):
        print(f"{prefix}Program (入口点)")
        for func in node.functions:
            print_annotated_tree(func, indent + 1)

    elif isinstance(node, FuncDef):
        params_str = ", ".join(f"{t} {n}" for t, n in node.params) if node.params else "void"
        print(f"{prefix}FuncDef (函数定义)")
        print(f"{child_prefix}返回类型: {node.return_type}")
        print(f"{child_prefix}函数名: {node.name}")
        print(f"{child_prefix}参数: [{params_str}]")
        print(f"{child_prefix}函数体:")
        print_annotated_tree(node.body, indent + 2)

    elif isinstance(node, Block):
        print(f"{prefix}Block (语句块)")
        for stmt in node.stmts:
            print_annotated_tree(stmt, indent + 1)

    elif isinstance(node, VarDecl):
        init_str = ""
        if node.init:
            init_str = " = "
            if isinstance(node.init, IntegerLit):
                init_str += str(node.init.value)
            elif isinstance(node.init, FloatLit):
                init_str += str(node.init.value)
            elif isinstance(node.init, CharLit):
                init_str += repr(node.init.value)
            else:
                init_str += "<expr>"
        print(f"{prefix}VarDecl (变量声明): {node.var_type} {node.name}{init_str}")

    elif isinstance(node, Assign):
        print(f"{prefix}Assign (赋值)")
        print(f"{child_prefix}左值:")
        print_annotated_tree(node.left, indent + 2)
        print(f"{child_prefix}右值 (表达式):")
        print_annotated_tree(node.right, indent + 2)

    elif isinstance(node, BinaryOp):
        op_desc = {
            '+': '加法', '-': '减法', '*': '乘法', '/': '除法', '%': '取模',
            '==': '等于', '!=': '不等于', '<': '小于', '>': '大于',
            '<=': '小于等于', '>=': '大于等于',
            '&&': '逻辑与 (短路)', '||': '逻辑或 (短路)',
        }
        desc = op_desc.get(node.op, node.op)
        print(f"{prefix}BinaryOp (二元运算): [{desc}]")
        print(f"{child_prefix}左操作数:")
        print_annotated_tree(node.left, indent + 2)
        print(f"{child_prefix}右操作数:")
        print_annotated_tree(node.right, indent + 2)

    elif isinstance(node, UnaryOp):
        op_desc = {'-': '取负', '!': '逻辑非'}
        desc = op_desc.get(node.op, node.op)
        print(f"{prefix}UnaryOp (一元运算): [{desc}]")
        print(f"{child_prefix}操作数:")
        print_annotated_tree(node.operand, indent + 2)

    elif isinstance(node, Identifier):
        print(f"{prefix}ID (标识符): {node.name}")

    elif isinstance(node, IntegerLit):
        print(f"{prefix}Int (整型字面量): {node.value}")

    elif isinstance(node, FloatLit):
        print(f"{prefix}Float (浮点字面量): {node.value}")

    elif isinstance(node, CharLit):
        print(f"{prefix}Char (字符字面量): {repr(node.value)}")

    elif isinstance(node, StringLit):
        print(f"{prefix}Str (字符串字面量): \"{node.value}\"")

    elif isinstance(node, IfStmt):
        print(f"{prefix}IfStmt (条件分支)")
        print(f"{child_prefix}条件:")
        print_annotated_tree(node.condition, indent + 2)
        print(f"{child_prefix}then 分支:")
        print_annotated_tree(node.then_stmt, indent + 2)
        if node.else_stmt:
            print(f"{child_prefix}else 分支:")
            print_annotated_tree(node.else_stmt, indent + 2)

    elif isinstance(node, WhileStmt):
        print(f"{prefix}WhileStmt (循环 — 先判断后执行)")
        print(f"{child_prefix}循环条件:")
        print_annotated_tree(node.condition, indent + 2)
        print(f"{child_prefix}循环体:")
        print_annotated_tree(node.body, indent + 2)

    elif isinstance(node, ForStmt):
        print(f"{prefix}ForStmt (循环 — 初始化+判断+更新)")
        print(f"{child_prefix}初始化:")
        if node.init:
            print_annotated_tree(node.init, indent + 2)
        else:
            print(f"{child_prefix}  <无>")
        print(f"{child_prefix}循环条件:")
        if node.condition:
            print_annotated_tree(node.condition, indent + 2)
        else:
            print(f"{child_prefix}  <无条件>")
        print(f"{child_prefix}更新:")
        if node.update:
            print_annotated_tree(node.update, indent + 2)
        else:
            print(f"{child_prefix}  <无>")
        print(f"{child_prefix}循环体:")
        print_annotated_tree(node.body, indent + 2)

    elif isinstance(node, CallStmt):
        print(f"{prefix}CallStmt (函数调用): {node.name}")
        for i, arg in enumerate(node.args):
            print(f"{child_prefix}参数{i}:")
            print_annotated_tree(arg, indent + 2)

    elif isinstance(node, ReturnStmt):
        if node.expr:
            print(f"{prefix}Return (返回)")
            print(f"{child_prefix}返回值:")
            print_annotated_tree(node.expr, indent + 2)
        else:
            print(f"{prefix}Return (返回) — 无返回值")

    elif isinstance(node, MemberAccess):
        print(f"{prefix}MemberAccess (成员访问): .{node.member}")
        print(f"{child_prefix}对象:")
        print_annotated_tree(node.object, indent + 2)

    elif isinstance(node, ArrayAccess):
        print(f"{prefix}ArrayAccess (数组下标)")
        print(f"{child_prefix}数组:")
        print_annotated_tree(node.array, indent + 2)
        print(f"{child_prefix}下标:")
        print_annotated_tree(node.index, indent + 2)

    elif isinstance(node, EmptyStmt):
        print(f"{prefix}EmptyStmt (空语句)")

    else:
        print(f"{prefix}<未知节点: {type(node).__name__}>")
