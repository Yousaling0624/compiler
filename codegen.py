import struct
from tac import TACOp


class CodeGenerator:
    def __init__(self, ir_result):
        self.functions = ir_result['functions']
        self.strings = ir_result['strings']
        self.float_constants = {}  # float_value → label
        self.float_counter = 0
        self.output = []
        self.pending_float_data = []

    def emit(self, line):
        self.output.append(line)

    def _get_float_label(self, value):
        if value not in self.float_constants:
            label = f"__float{self.float_counter}"
            self.float_counter += 1
            self.float_constants[value] = label
            # Store float as 32-bit hex
            bits = struct.unpack('<I', struct.pack('<f', float(value)))[0]
            self.pending_float_data.append((label, bits))
        return self.float_constants[value]

    def generate(self):
        # Pre-scan: collect all float constants from TAC instructions
        for func_info in self.functions.values():
            self._prescan_float_constants(func_info['tac'], func_info.get('var_types', {}))

        self.emit(".intel_syntax noprefix")
        self.emit(".section .data")
        # Emit string literals
        for sid in sorted(self.strings.keys()):
            content = self.strings[sid]
            escaped = content.replace('\\', '\\\\').replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
            self.emit(f"{sid}: .asciz \"{escaped}\"")

        # Emit float constants
        for label, bits in self.pending_float_data:
            self.emit(f"{label}: .long {bits}")

        self.emit("")
        self.emit(".section .text")
        self.emit(".extern printf")
        self.emit(".extern scanf")
        self.emit("")

        for func_name, func_info in self.functions.items():
            self.generate_function(func_name, func_info)

        return '\n'.join(self.output)

    def _prescan_float_constants(self, tac_list, var_types):
        """Pre-scan TAC to discover float constants before emitting data section."""
        for instr in tac_list:
            if instr.op == TACOp.COPY and var_types.get(instr.dest, 'int') == 'float':
                if self._is_number(instr.src1):
                    self._get_float_label(float(instr.src1))
            elif instr.op == TACOp.ASSIGN:
                result_type = 'float' if 'float' in (
                    var_types.get(instr.src1, 'int'),
                    var_types.get(instr.src2, 'int')) else 'int'
                if result_type == 'float':
                    for src in (instr.src1, instr.src2):
                        if self._is_number(src):
                            self._get_float_label(float(src))
            elif instr.op == TACOp.UNARY and instr.op_str == '-':
                if var_types.get(instr.src1, 'int') == 'float':
                    self._get_float_label(-0.0)

    def generate_function(self, name, info):
        tac_list = info['tac']
        var_types = info.get('var_types', {})

        # Collect stack variables
        stack_vars = self._collect_stack_vars(tac_list, var_types)
        offsets = {}
        offset = 8
        for var in sorted(stack_vars):
            offsets[var] = offset
            offset += 8

        frame_size = ((offset - 8 + 15) // 16) * 16

        # Prologue
        if name == "main":
            self.emit(f".globl {name}")
        self.emit(f"{name}:")
        self.emit("    push rbp")
        self.emit("    mov rbp, rsp")
        if frame_size > 0:
            self.emit(f"    sub rsp, {frame_size}")

        params_buffer = []
        for instr in tac_list:
            if instr.op == TACOp.PARAM:
                params_buffer.append(instr.src1)
            elif instr.op == TACOp.CALL:
                self._emit_call(instr, params_buffer, offsets, var_types)
                params_buffer = []
            else:
                self._emit_instr(instr, offsets, var_types, name)

        self.emit("")

    def _collect_stack_vars(self, tac_list, var_types):
        vars_set = set()
        for instr in tac_list:
            for attr in ('dest', 'src1', 'src2'):
                val = getattr(instr, attr, None)
                if self._needs_stack(val):
                    vars_set.add(val)
        return vars_set

    def _needs_stack(self, name):
        if not isinstance(name, str):
            return False
        if not name:
            return False
        # Labels
        if name.startswith('L') and name[1:].isdigit():
            return False
        # String IDs
        if name.startswith('str') and name[3:].isdigit():
            return False
        # Float constant labels
        if name.startswith('__float'):
            return False
        # Numeric literals
        try:
            float(name)
            return False
        except ValueError:
            pass
        # Function names
        if name in ('printf', 'scanf'):
            return False
        return True

    # ==================== Instruction emission ====================

    def _emit_instr(self, instr, offsets, var_types, func_name):
        op = instr.op
        if op == TACOp.LABEL:
            self.emit(f"{instr.dest}:")
        elif op == TACOp.GOTO:
            self.emit(f"    jmp {instr.dest}")
        elif op == TACOp.IF_GOTO:
            self._emit_if_goto(instr, offsets, var_types)
        elif op == TACOp.IF_FALSE_GOTO:
            self._emit_if_false_goto(instr, offsets, var_types)
        elif op == TACOp.COPY:
            self._emit_copy(instr, offsets, var_types)
        elif op == TACOp.ASSIGN:
            self._emit_assign_op(instr, offsets, var_types)
        elif op == TACOp.UNARY:
            self._emit_unary_op(instr, offsets, var_types)
        elif op == TACOp.RETURN:
            self._emit_return(instr, offsets, var_types)
        elif op == TACOp.ADDR:
            self._emit_addr(instr, offsets, var_types)

    def _emit_if_goto(self, instr, offsets, var_types):
        self._load_src_to_rax(instr.src1, offsets, var_types)
        self.emit("    cmp rax, 0")
        self.emit(f"    jne {instr.dest}")

    def _emit_if_false_goto(self, instr, offsets, var_types):
        self._load_src_to_rax(instr.src1, offsets, var_types)
        self.emit("    cmp rax, 0")
        self.emit(f"    je {instr.dest}")

    def _emit_copy(self, instr, offsets, var_types):
        dest_type = var_types.get(instr.dest, 'int')
        if dest_type == 'float':
            self._load_float_to_xmm0(instr.src1, offsets)
            self._store_xmm0(instr.dest, offsets)
        else:
            self._load_src_to_rax(instr.src1, offsets, var_types)
            self._store_rax(instr.dest, offsets)

    def _emit_assign_op(self, instr, offsets, var_types):
        op_str = instr.op_str
        src1_type = var_types.get(instr.src1, 'int')
        src2_type = var_types.get(instr.src2, 'int')
        result_type = 'float' if 'float' in (src1_type, src2_type) else 'int'

        if op_str in ('+', '-', '*', '/'):
            if result_type == 'float':
                self._float_arithmetic(instr, offsets, var_types, op_str)
            else:
                self._int_arithmetic(instr, offsets, var_types, op_str)
        elif op_str == '%':
            self._int_arithmetic(instr, offsets, var_types, op_str)
        elif op_str in ('==', '!=', '<', '>', '<=', '>='):
            if result_type == 'float':
                self._float_compare(instr, offsets, var_types, op_str)
            else:
                self._int_compare(instr, offsets, var_types, op_str)

    def _emit_unary_op(self, instr, offsets, var_types):
        op_str = instr.op_str
        if op_str == '-':
            src_type = var_types.get(instr.src1, 'int')
            if src_type == 'float':
                self._load_float_to_xmm0(instr.src1, offsets)
                # Negate float: XOR sign bit
                fid = self._get_float_label(-0.0)
                self.emit(f"    xorps xmm0, [rip + {fid}]")
                self._store_xmm0(instr.dest, offsets)
            else:
                self._load_src_to_rax(instr.src1, offsets, var_types)
                self.emit("    neg rax")
                self._store_rax(instr.dest, offsets)
        elif op_str == '!':
            self._load_src_to_rax(instr.src1, offsets, var_types)
            self.emit("    cmp rax, 0")
            self.emit("    sete al")
            self.emit("    movzx rax, al")
            self._store_rax(instr.dest, offsets)

    def _emit_return(self, instr, offsets, var_types):
        if instr.src1:
            self._load_src_to_rax(instr.src1, offsets, var_types)
        self.emit("    mov rsp, rbp")
        self.emit("    pop rbp")
        self.emit("    ret")

    def _emit_addr(self, instr, offsets, var_types):
        off = offsets.get(instr.src1, 0)
        self.emit(f"    lea rax, [rbp - {off}]")
        self._store_rax(instr.dest, offsets)

    # ==================== Integer arithmetic ====================

    def _int_arithmetic(self, instr, offsets, var_types, op_str):
        if op_str in ('+', '-'):
            self._load_src_to_rax(instr.src1, offsets, var_types)
            if op_str == '+':
                self._add_to_rax(instr.src2, offsets, var_types)
            else:
                self._sub_from_rax(instr.src2, offsets, var_types)
            self._store_rax(instr.dest, offsets)
        elif op_str == '*':
            self._load_src_to_rax(instr.src1, offsets, var_types)
            self._mul_rax(instr.src2, offsets, var_types)
            self._store_rax(instr.dest, offsets)
        elif op_str == '/':
            self.emit("    xor edx, edx")
            self._load_src_to_rax(instr.src1, offsets, var_types)
            self.emit("    cqo")
            self._idiv_rax(instr.src2, offsets, var_types)
            self._store_rax(instr.dest, offsets)
        elif op_str == '%':
            self.emit("    xor edx, edx")
            self._load_src_to_rax(instr.src1, offsets, var_types)
            self.emit("    cqo")
            self._idiv_rax(instr.src2, offsets, var_types)
            if instr.dest in offsets:
                self.emit(f"    mov [rbp - {offsets[instr.dest]}], rdx")

    def _int_compare(self, instr, offsets, var_types, op_str):
        self._load_src_to_rax(instr.src1, offsets, var_types)
        self._cmp_rax(instr.src2, offsets, var_types)
        cond_map = {'==': 'e', '!=': 'ne', '<': 'l', '>': 'g', '<=': 'le', '>=': 'ge'}
        cc = cond_map.get(op_str, 'e')
        self.emit(f"    set{cc} al")
        self.emit("    movzx rax, al")
        self._store_rax(instr.dest, offsets)

    # ==================== Float arithmetic ====================

    def _float_arithmetic(self, instr, offsets, var_types, op_str):
        self._load_float_to_xmm0(instr.src1, offsets)
        if op_str == '+':
            self._addss_xmm0(instr.src2, offsets, var_types)
        elif op_str == '-':
            self._subss_xmm0(instr.src2, offsets, var_types)
        elif op_str == '*':
            self._mulss_xmm0(instr.src2, offsets, var_types)
        elif op_str == '/':
            self._divss_xmm0(instr.src2, offsets, var_types)
        self._store_xmm0(instr.dest, offsets)

    def _float_compare(self, instr, offsets, var_types, op_str):
        self._load_float_to_xmm0(instr.src1, offsets)
        self._ucomiss_xmm0(instr.src2, offsets, var_types)
        cond_map = {'==': 'e', '!=': 'ne', '<': 'b', '>': 'a', '<=': 'be', '>=': 'ae'}
        cc = cond_map.get(op_str, 'e')
        self.emit(f"    set{cc} al")
        self.emit("    movzx rax, al")
        self._store_rax(instr.dest, offsets)

    # ==================== Function calls ====================

    def _emit_call(self, instr, params, offsets, var_types):
        func = instr.src1
        regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

        for i, param in enumerate(params):
            if i < len(regs):
                self._load_param_to_reg(regs[i], param, offsets, var_types)
            else:
                self._load_src_to_rax(param, offsets, var_types)
                self.emit("    push rax")

        self.emit("    xor eax, eax")
        self.emit(f"    call {func}")

        extra = max(0, len(params) - len(regs))
        if extra > 0:
            self.emit(f"    add rsp, {extra * 8}")

        if instr.dest:
            self._store_rax(instr.dest, offsets)

    # ==================== Load helpers ====================

    def _load_src_to_rax(self, src, offsets, var_types):
        if src is None:
            self.emit("    xor eax, eax")
        elif self._is_number(src):
            self.emit(f"    mov rax, {src}")
        elif src.startswith('str') and src[3:].isdigit():
            self.emit(f"    lea rax, [rip + {src}]")
        elif src in offsets:
            self.emit(f"    mov rax, [rbp - {offsets[src]}]")
        else:
            self.emit(f"    mov rax, {src}")

    def _load_param_to_reg(self, reg, src, offsets, var_types):
        if self._is_number(src):
            self.emit(f"    mov {reg}, {src}")
        elif src.startswith('str') and src[3:].isdigit():
            self.emit(f"    lea {reg}, [rip + {src}]")
        elif src in offsets:
            self.emit(f"    mov {reg}, [rbp - {offsets[src]}]")
        else:
            self.emit(f"    mov {reg}, {src}")

    def _store_rax(self, dest, offsets):
        if dest in offsets:
            self.emit(f"    mov [rbp - {offsets[dest]}], rax")

    def _add_to_rax(self, src, offsets, var_types):
        if self._is_number(src):
            self.emit(f"    add rax, {src}")
        elif src in offsets:
            self.emit(f"    add rax, [rbp - {offsets[src]}]")

    def _sub_from_rax(self, src, offsets, var_types):
        if self._is_number(src):
            self.emit(f"    sub rax, {src}")
        elif src in offsets:
            self.emit(f"    sub rax, [rbp - {offsets[src]}]")

    def _mul_rax(self, src, offsets, var_types):
        if self._is_number(src):
            self.emit(f"    mov rcx, {src}")
            self.emit("    imul rax, rcx")
        elif src in offsets:
            self.emit(f"    imul rax, [rbp - {offsets[src]}]")

    def _idiv_rax(self, src, offsets, var_types):
        if self._is_number(src):
            self.emit(f"    mov rcx, {src}")
            self.emit("    idiv rcx")
        elif src in offsets:
            self.emit(f"    mov rcx, [rbp - {offsets[src]}]")
            self.emit("    idiv rcx")

    def _cmp_rax(self, src, offsets, var_types):
        if self._is_number(src):
            self.emit(f"    cmp rax, {src}")
        elif src in offsets:
            self.emit(f"    cmp rax, [rbp - {offsets[src]}]")

    # ==================== Float load/store helpers ====================

    def _load_float_to_xmm0(self, src, offsets):
        if self._is_number(src):
            fl = self._get_float_label(float(src))
            self.emit(f"    movss xmm0, [rip + {fl}]")
        elif src in offsets:
            self.emit(f"    movss xmm0, [rbp - {offsets[src]}]")

    def _store_xmm0(self, dest, offsets):
        if dest in offsets:
            self.emit(f"    movss [rbp - {offsets[dest]}], xmm0")

    def _addss_xmm0(self, src, offsets, var_types):
        if self._is_number(src):
            fl = self._get_float_label(float(src))
            self.emit(f"    addss xmm0, [rip + {fl}]")
        elif src in offsets:
            self.emit(f"    addss xmm0, [rbp - {offsets[src]}]")

    def _subss_xmm0(self, src, offsets, var_types):
        if self._is_number(src):
            fl = self._get_float_label(float(src))
            self.emit(f"    subss xmm0, [rip + {fl}]")
        elif src in offsets:
            self.emit(f"    subss xmm0, [rbp - {offsets[src]}]")

    def _mulss_xmm0(self, src, offsets, var_types):
        if self._is_number(src):
            fl = self._get_float_label(float(src))
            self.emit(f"    mulss xmm0, [rip + {fl}]")
        elif src in offsets:
            self.emit(f"    mulss xmm0, [rbp - {offsets[src]}]")

    def _divss_xmm0(self, src, offsets, var_types):
        if self._is_number(src):
            fl = self._get_float_label(float(src))
            self.emit(f"    divss xmm0, [rip + {fl}]")
        elif src in offsets:
            self.emit(f"    divss xmm0, [rbp - {offsets[src]}]")

    def _ucomiss_xmm0(self, src, offsets, var_types):
        if self._is_number(src):
            fl = self._get_float_label(float(src))
            self.emit(f"    ucomiss xmm0, [rip + {fl}]")
        elif src in offsets:
            self.emit(f"    ucomiss xmm0, [rbp - {offsets[src]}]")

    # ==================== Utility ====================

    def _is_number(self, val):
        if not isinstance(val, str):
            return False
        try:
            float(val)
            return True
        except ValueError:
            return False
