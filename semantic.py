from tac import TACInstr, TACOp
from ast_nodes import (
    Program, FuncDef, Block, VarDecl, Assign, BinaryOp, UnaryOp,
    Identifier, IntegerLit, FloatLit, CharLit, StringLit,
    IfStmt, WhileStmt, ForStmt, CallStmt, ReturnStmt, EmptyStmt
)


class SemanticError(Exception):
    def __init__(self, msg):
        super().__init__(f"Semantic error: {msg}")


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}     # var_name → {'type': str, 'tac_name': str}
        self.temp_types = {}       # temp_name → type_str
        self.tac_code = []         # list of TACInstr for current function
        self.strings = {}          # string_id → content
        self.string_counter = 0
        self.temp_counter = 0
        self.label_counter = 0
        self.current_func_name = ""

    def new_temp(self, type_hint='int'):
        name = f"t{self.temp_counter}"
        self.temp_counter += 1
        self.temp_types[name] = type_hint
        return name

    def new_label(self):
        name = f"L{self.label_counter}"
        self.label_counter += 1
        return name

    def new_string_id(self, content):
        sid = f"str{self.string_counter}"
        self.string_counter += 1
        self.strings[sid] = content
        return sid

    def emit(self, op, dest=None, src1=None, src2=None, op_str=None):
        instr = TACInstr(op, dest=dest, src1=src1, src2=src2, op_str=op_str)
        self.tac_code.append(instr)
        return instr

    def lookup(self, name):
        if name in self.symbol_table:
            return self.symbol_table[name]
        raise SemanticError(f"Undefined variable '{name}'")

    def declare(self, name, var_type, tac_name=None):
        if name in self.symbol_table:
            raise SemanticError(f"Variable '{name}' already declared")
        tac_name = tac_name or name
        self.symbol_table[name] = {'type': var_type, 'tac_name': tac_name}

    # ============ Entry ============

    def analyze(self, program):
        result = {'functions': {}, 'strings': {}}
        for func_def in program.functions:
            func_tac, func_strings, var_types = self.analyze_function(func_def)
            result['functions'][func_def.name] = {
                'tac': func_tac,
                'return_type': func_def.return_type,
                'params': func_def.params,
                'var_types': var_types,
            }
            result['strings'].update(func_strings)
        result['strings'].update(self.strings)
        return result

    def analyze_function(self, func_def):
        self.symbol_table = {}
        self.temp_types = {}
        self.tac_code = []
        self.temp_counter = 0
        self.label_counter = 0
        self.current_func_name = func_def.name
        self.strings = {}

        # Declare parameters
        for ptype, pname in func_def.params:
            self.declare(pname, ptype)

        self.emit_block(func_def.body)

        # Ensure main returns 0 if no explicit return
        if func_def.name == "main":
            has_return = any(instr.op == TACOp.RETURN for instr in self.tac_code)
            if not has_return:
                self.emit(TACOp.RETURN, src1='0')

        var_types = {name: info['type'] for name, info in self.symbol_table.items()}
        var_types.update(self.temp_types)
        return self.tac_code, self.strings, var_types

    def _get_type(self, name):
        """Look up the type of a value (variable, temp, or literal)."""
        if name in self.symbol_table:
            return self.symbol_table[name]['type']
        if name in self.temp_types:
            return self.temp_types[name]
        # Literals
        try:
            float(name)
            return 'float' if '.' in name else 'int'
        except ValueError:
            pass
        return 'int'

    # ============ Block ============

    def emit_block(self, block):
        for stmt in block.stmts:
            self.emit_stmt(stmt)

    def emit_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            return self.emit_var_decl(stmt)
        elif isinstance(stmt, Assign):
            self.emit_assign(stmt)
        elif isinstance(stmt, BinaryOp):
            self.emit_expr(stmt)
        elif isinstance(stmt, UnaryOp):
            self.emit_expr(stmt)
        elif isinstance(stmt, CallStmt):
            if stmt.name in ('printf', 'scanf'):
                self.emit_io_call(stmt)
            else:
                self.emit_user_call(stmt)
        elif isinstance(stmt, IfStmt):
            self.emit_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self.emit_while(stmt)
        elif isinstance(stmt, ForStmt):
            self.emit_for(stmt)
        elif isinstance(stmt, ReturnStmt):
            self.emit_return(stmt)
        elif isinstance(stmt, Block):
            self.emit_block(stmt)
        elif isinstance(stmt, EmptyStmt):
            pass

    # ============ Variable Declaration ============

    def emit_var_decl(self, decl):
        self.declare(decl.name, decl.var_type)
        if decl.init is not None:
            val = self.emit_expr(decl.init)
            self.emit(TACOp.COPY, dest=decl.name, src1=val)

    # ============ Assignment ============

    def emit_assign(self, assign):
        if not isinstance(assign.left, Identifier):
            raise SemanticError("Can only assign to a variable")
        self.lookup(assign.left.name)  # verify exists
        val = self.emit_expr(assign.right)
        self.emit(TACOp.COPY, dest=assign.left.name, src1=val)

    # ============ Expressions ============

    def emit_expr(self, node):
        """Generate code to compute a value, return the temp/variable name."""
        if isinstance(node, IntegerLit):
            return str(node.value)
        elif isinstance(node, FloatLit):
            return str(node.value)
        elif isinstance(node, CharLit):
            return str(ord(node.value))
        elif isinstance(node, StringLit):
            sid = self.new_string_id(node.value)
            return sid
        elif isinstance(node, Identifier):
            self.lookup(node.name)
            return node.name
        elif isinstance(node, UnaryOp):
            src = self.emit_expr(node.operand)
            src_type = self._get_type(src)
            dest = self.new_temp('int' if node.op == '!' else src_type)
            self.emit(TACOp.UNARY, dest=dest, src1=src, op_str=node.op)
            return dest
        elif isinstance(node, BinaryOp):
            return self.emit_binary_op(node)
        elif isinstance(node, CallStmt):
            return self.emit_call_expr(node)
        raise SemanticError(f"Unknown expression node: {type(node).__name__}")

    def emit_binary_op(self, node):
        if node.op in ('&&', '||'):
            return self.emit_logical_value(node)
        left = self.emit_expr(node.left)
        right = self.emit_expr(node.right)
        left_type = self._get_type(left)
        right_type = self._get_type(right)
        result_type = 'float' if ('float' in (left_type, right_type)) else 'int'
        dest = self.new_temp(result_type)
        self.emit(TACOp.ASSIGN, dest=dest, src1=left, src2=right, op_str=node.op)
        return dest

    def emit_logical_value(self, node):
        """Generate code that produces 1 or 0 for && and ||."""
        dest = self.new_temp('int')
        true_label = self.new_label()
        false_label = self.new_label()
        end_label = self.new_label()
        self.emit_jumping_code(node, true_label, false_label)
        self.emit(TACOp.LABEL, dest=true_label)
        self.emit(TACOp.COPY, dest=dest, src1='1')
        self.emit(TACOp.GOTO, dest=end_label)
        self.emit(TACOp.LABEL, dest=false_label)
        self.emit(TACOp.COPY, dest=dest, src1='0')
        self.emit(TACOp.LABEL, dest=end_label)
        return dest

    def emit_jumping_code(self, node, true_label, false_label):
        """Emit jumping code for a boolean expression.
        Falls through to true_label, jumps to false_label."""
        if isinstance(node, BinaryOp) and node.op == '&&':
            mid = self.new_label()
            self.emit_jumping_code(node.left, mid, false_label)
            self.emit(TACOp.LABEL, dest=mid)
            self.emit_jumping_code(node.right, true_label, false_label)
        elif isinstance(node, BinaryOp) and node.op == '||':
            mid = self.new_label()
            self.emit_jumping_code(node.left, true_label, mid)
            self.emit(TACOp.LABEL, dest=mid)
            self.emit_jumping_code(node.right, true_label, false_label)
        elif isinstance(node, UnaryOp) and node.op == '!':
            self.emit_jumping_code(node.operand, false_label, true_label)
        else:
            cond = self.emit_expr(node)
            self.emit(TACOp.IF_GOTO, dest=true_label, src1=cond)
            self.emit(TACOp.GOTO, dest=false_label)

    # ============ If / While / For ============

    def emit_if(self, node):
        if node.else_stmt:
            else_label = self.new_label()
            end_label = self.new_label()
            self.emit_condition(node.condition, else_label)
            self.emit_stmt(node.then_stmt)
            self.emit(TACOp.GOTO, dest=end_label)
            self.emit(TACOp.LABEL, dest=else_label)
            self.emit_stmt(node.else_stmt)
            self.emit(TACOp.LABEL, dest=end_label)
        else:
            end_label = self.new_label()
            self.emit_condition(node.condition, end_label)
            self.emit_stmt(node.then_stmt)
            self.emit(TACOp.LABEL, dest=end_label)

    def emit_condition(self, node, false_label, jump_on_false=True):
        """Emit code to evaluate condition and jump to false_label if false."""
        # Use short-circuit jumping code for && and ||, value+IF_FALSE_GOTO for others
        if isinstance(node, BinaryOp) and node.op == '&&':
            self._emit_sc_and(node, false_label)
        elif isinstance(node, BinaryOp) and node.op == '||':
            self._emit_sc_or(node, false_label)
        else:
            cond = self.emit_expr(node)
            self.emit(TACOp.IF_FALSE_GOTO, dest=false_label, src1=cond)

    def _emit_sc_and(self, node, false_label):
        """Short-circuit AND: if left is false, jump to false_label; else check right."""
        self.emit_condition(node.left, false_label)
        self.emit_condition(node.right, false_label)

    def _emit_sc_or(self, node, false_label):
        """Short-circuit OR: if left is true, fall through; if right is false, jump."""
        body_label = self.new_label()
        cond = self.emit_expr(node.left)
        self.emit(TACOp.IF_GOTO, dest=body_label, src1=cond)
        self.emit_condition(node.right, false_label)
        self.emit(TACOp.LABEL, dest=body_label)

    def emit_while(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        self.emit(TACOp.LABEL, dest=start_label)
        self.emit_condition(node.condition, end_label, jump_on_false=True)
        self.emit_stmt(node.body)
        self.emit(TACOp.GOTO, dest=start_label)
        self.emit(TACOp.LABEL, dest=end_label)

    def emit_for(self, node):
        start_label = self.new_label()
        end_label = self.new_label()

        if node.init is not None:
            self.emit_stmt(node.init)

        self.emit(TACOp.LABEL, dest=start_label)
        if node.condition is not None:
            self.emit_condition(node.condition, end_label)

        self.emit_stmt(node.body)

        if node.update is not None:
            self.emit_stmt(node.update)

        self.emit(TACOp.GOTO, dest=start_label)
        self.emit(TACOp.LABEL, dest=end_label)

    # ============ Return ============

    def emit_return(self, node):
        if node.expr:
            val = self.emit_expr(node.expr)
            self.emit(TACOp.RETURN, src1=val)
        else:
            self.emit(TACOp.RETURN)

    # ============ I/O Calls ============

    def emit_io_call(self, node):
        if node.name == 'printf':
            fmt = node.args[0].value if isinstance(node.args[0], StringLit) else ""
            # Emit PARAM for each argument (after format string)
            for arg in node.args:
                val = self.emit_expr(arg)
                self.emit(TACOp.PARAM, src1=val)
            self.emit(TACOp.CALL, src1='printf', src2=len(node.args))
        elif node.name == 'scanf':
            fmt = node.args[0].value if isinstance(node.args[0], StringLit) else ""
            # Emit format string param
            fmt_val = self.emit_expr(node.args[0])
            self.emit(TACOp.PARAM, src1=fmt_val)
            # Emit address-of for each variable
            for arg in node.args[1:]:
                if isinstance(arg, Identifier):
                    self.lookup(arg.name)
                    addr_temp = self.new_temp()
                    self.emit(TACOp.ADDR, dest=addr_temp, src1=arg.name)
                    self.emit(TACOp.PARAM, src1=addr_temp)
                else:
                    val = self.emit_expr(arg)
                    self.emit(TACOp.PARAM, src1=val)
            self.emit(TACOp.CALL, src1='scanf', src2=len(node.args))

    def emit_call_expr(self, node):
        for arg in node.args:
            val = self.emit_expr(arg)
            self.emit(TACOp.PARAM, src1=val)
        dest = self.new_temp('int')
        self.emit(TACOp.CALL, dest=dest, src1=node.name, src2=len(node.args))
        return dest

    def emit_user_call(self, node):
        for arg in node.args:
            val = self.emit_expr(arg)
            self.emit(TACOp.PARAM, src1=val)
        self.emit(TACOp.CALL, src1=node.name, src2=len(node.args))
