import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Lexer import MainController
from DynamicLL1 import Grammar, DynamicLL1Parser

class SymbolType:
    INT = "int"
    FLOAT = "float"
    CHAR = "char"
    VOID = "void"
    STRUCT = "struct"
    ARRAY = "array"
    POINTER = "pointer"

class Symbol:
    def __init__(self, name, type_name, scope, line, col):
        self.name = name
        self.type = type_name
        self.scope = scope
        self.line = line
        self.col = col

class StructDef:
    def __init__(self, name):
        self.name = name
        self.fields = {}

class SymbolTable:
    def __init__(self):
        self.scope_level = 0
        self.globals = {}
        self.locals = {}
        self.structs = {}
    def enter(self): self.scope_level += 1
    def exit(self): self.scope_level -= 1
    def add_struct(self, s): self.structs[s.name] = s
    def add_var(self, name, typ, line, col):
        if self.scope_level == 0:
            self.globals[name] = Symbol(name, typ, 0, line, col)
        else:
            self.locals[name] = Symbol(name, typ, self.scope_level, line, col)
    def find(self, name):
        if name in self.locals: return self.locals[name]
        if name in self.globals: return self.globals[name]
        return None

# ====================== 核心：三元式 IR ======================
class IR:
    def __init__(self, op, arg1=None, arg2=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"({self.op}, {self.arg1 if self.arg1 is not None else '-'}, {self.arg2 if self.arg2 is not None else '-'})"

class SemanticAnalyzer:
    def __init__(self, parser):
        self.parser = parser
        self.sym = SymbolTable()
        self.ir = []
        self.errors = []
        self.brace_stack = []
        self.label_count = 0
        self.temp_count = 0
        self.in_function = False
        self.flag_error_reported = False  # 防止重复报错

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def err(self, msg, line, col):
        if line <= 0: line = 1
        if col <= 0: col = 1
        self.errors.append((line, col, msg))
        print(f"[语义错误] 行{line}列{col}：{msg}", flush=True)

    def parse_expr(self, tokens, i, n):
        expr_start = i
        while i < n and tokens[i].value not in (";", ")", "}", "else", "{", "]", "\n"):
            i += 1
        expr_tokens = tokens[expr_start:i]
        expr_str = " ".join([t.value for t in expr_tokens]).strip()

        for tok in expr_tokens:
            if tok.value not in ("=", "+", "-", "*", "/", "<", ">", "==", "!=", "[", "]", ".", "(", ")", "140", "1", "-1", "flag"):
                if not self.sym.find(tok.value):
                    self.err(f"变量 '{tok.value}' 未定义", tok.line, tok.col)
        
        temp = self.new_temp()
        self.ir.append(IR("=", expr_str, temp))
        return temp, i, expr_str

    def analyze(self):
        print(">>> 开始语义分析 & 三元式中间代码生成 <<<\n", flush=True)
        tokens = self.parser.tokens
        n = len(tokens)
        i = 0
        
        # 结构体字段顺序
        struct_fields = ["name", "num", "age", "score"]
        
        while i < n:
            tok = tokens[i]
            v = tok.value
            line = tok.line
            col = tok.col

            if v == "{":
                self.brace_stack.append(line)
                i += 1
            elif v == "}":
                if self.brace_stack:
                    self.brace_stack.pop()
                i += 1
            
            # 结构体定义 - 检测 struct student {
            elif v == "struct" and i+1 < n and tokens[i+1].value == "student" and i+2 < n and tokens[i+2].value == "{":
                i += 1  # 跳过 struct
                s_name = tokens[i].value  # student
                i += 1  # 跳过 student
                i += 1  # 跳过 {
                
                st = StructDef(s_name)
                
                # 解析字段
                while i < n and tokens[i].value != "}":
                    if tokens[i].value in (";", ","):
                        i += 1
                        continue
                    if tokens[i].value in ("char", "int", "float"):
                        f_type = tokens[i].value
                        i += 1
                        # 处理指针 char*
                        if i < n and tokens[i].value == "*":
                            f_type = "char*"
                            i += 1
                        if i < n:
                            f_name = tokens[i].value
                            st.fields[f_name] = f_type
                            print(f"  字段: {f_name} -> {f_type}")
                            i += 1
                    else:
                        i += 1
                
                i += 1  # 跳过 }
                
                # 检查分号 - 不自动补全，直接报错
                if i < n and tokens[i].value == ";":
                    i += 1
                    print(f" 结构体定义完成：struct {s_name}，字段：{list(st.fields.keys())}")
                else:
                    self.err("结构体定义末尾缺少分号 ';'", line, col)
                
                self.sym.add_struct(st)
                continue

            # 处理 struct student sts[2] = {...} 结构体数组初始化（必须带struct关键字）
            elif v == "struct" and i+1 < n and tokens[i+1].value == "student":
                i += 2  # 跳过 struct student
                if i < n:
                    array_name = tokens[i].value  # sts
                    i += 1
                    
                    # 解析数组 [2]
                    array_size = 2
                    if i < n and tokens[i].value == "[":
                        i += 1
                        if i < n and tokens[i].value.isdigit():
                            array_size = int(tokens[i].value)
                            i += 1
                        if i < n and tokens[i].value == "]":
                            i += 1
                    
                    self.sym.add_var(array_name, "struct student[]", line, col)
                    print(f" 结构体数组声明：{array_name}[{array_size}]")
                    
                    # 处理初始化 = {...}
                    if i < n and tokens[i].value == "=":
                        i += 1
                        if i < n and tokens[i].value == "{":
                            i += 1
                            
                            idx = 0
                            while i < n and tokens[i].value != "}" and idx < array_size:
                                # 跳过逗号
                                if tokens[i].value == ",":
                                    i += 1
                                    continue
                                
                                # 处理每个结构体元素 {...}
                                if tokens[i].value == "{":
                                    i += 1
                                    field_idx = 0
                                    
                                    while i < n and tokens[i].value != "}":
                                        if tokens[i].value == ",":
                                            i += 1
                                            continue
                                        
                                        value = tokens[i].value
                                        i += 1
                                        
                                        if field_idx < len(struct_fields):
                                            field_name = struct_fields[field_idx]
                                            lvalue = f"{array_name}[{idx}].{field_name}"
                                            self.ir.append(IR("=", value, lvalue))
                                            print(f"   生成: (=, {value}, {lvalue})")
                                        field_idx += 1
                                    
                                    i += 1  # 跳过 }
                                    idx += 1
                                else:
                                    i += 1
                            
                            i += 1  # 跳过最后的 }
                    
                    # 跳过到分号
                    while i < n and tokens[i].value != ";":
                        i += 1
                    if i < n:
                        i += 1
                    continue
            
            # 检测缺少 struct 关键字的错误 - student sts[2]
            elif v == "student" and i+1 < n and tokens[i+1].value == "sts":
                self.err("结构体类型缺少 'struct' 关键字，应为 'struct student sts[2]'", line, col)
                # 跳过这个错误的声明
                i += 1
                continue

            elif v == "void" and i+1 < n and tokens[i+1].value == "main":
                self.sym.enter()
                self.in_function = True
                self.flag_error_reported = False  # 重置标志
                self.ir.append(IR("func", None, "main"))
                print(" 进入函数：main")
                i += 2

            # 变量声明
            elif v in ["int", "float", "char"]:
                t = v
                i += 1
                prev_var = ""
                while i < n and tokens[i].value not in (";", "}"):
                    var_name = tokens[i].value
                    if var_name == ",":
                        i += 1
                        continue
                    if var_name == "=":
                        i += 1
                        val = tokens[i].value
                        if val == "-" and i+1 < n:
                            val = "-" + tokens[i+1].value
                            i += 1
                        self.ir.append(IR("=", val, prev_var))
                        print(f" 变量初始化：{prev_var} = {val}")
                        i += 1
                        continue
                    prev_var = var_name
                    self.sym.add_var(var_name, t, line, col)
                    print(f" 变量声明：{t} {var_name}")
                    i += 1
                if i < n and tokens[i].value == ";":
                    i += 1

            elif v == "if":
                i += 1
                if i < n and tokens[i].value == "(":
                    i += 1
                cond_parts = []
                while i < n and tokens[i].value != ")":
                    cond_parts.append(tokens[i].value)
                    i += 1
                cond_expr = " ".join(cond_parts)
                i += 1

                cond_temp = self.new_temp()
                self.ir.append(IR("=", cond_expr, cond_temp))
                label_true = self.new_label()
                label_false = self.new_label()
                label_end = self.new_label()

                self.ir.append(IR("if", cond_temp, label_true))
                self.ir.append(IR("goto", None, label_false))
                self.ir.append(IR("label", None, label_true))
                print(f" 生成if条件：if {cond_temp} goto {label_true}")

                while i < n and tokens[i].value not in ("else", "}"):
                    if tokens[i].value == ";":
                        i += 1
                        continue
                    if tokens[i].value == "flag":
                        if not self.sym.find("flag") and not self.flag_error_reported:
                            self.err("变量 'flag' 未声明", line, col)
                            self.flag_error_reported = True
                        expr_temp, i, expr_str = self.parse_expr(tokens, i, n)
                        if "=" in expr_str:
                            val = expr_str.split("=")[1].strip()
                            self.ir.append(IR("=", val, "flag"))
                            print(f" 赋值：{expr_str}")
                    else:
                        i += 1

                self.ir.append(IR("goto", None, label_end))
                self.ir.append(IR("label", None, label_false))

                if i < n and tokens[i].value == "else":
                    i += 1
                    while i < n and tokens[i].value not in (";", "}"):
                        if tokens[i].value == "flag":
                            if not self.sym.find("flag") and not self.flag_error_reported:
                                self.err("变量 'flag' 未声明", line, col)
                                self.flag_error_reported = True
                            expr_temp, i, expr_str = self.parse_expr(tokens, i, n)
                            if "=" in expr_str:
                                val = expr_str.split("=")[1].strip()
                                self.ir.append(IR("=", val, "flag"))
                                print(f" 赋值：{expr_str}")
                        else:
                            i += 1
                    if i < n and tokens[i].value == ";":
                        i += 1

                self.ir.append(IR("label", None, label_end))
                print(f" if/else 结束标签：{label_end}")

            # printf 处理
            elif v == "printf":
                i += 1
                if i < n and tokens[i].value == "(":
                    i += 1
                    if i < n:
                        fmt_str = tokens[i].value
                        self.ir.append(IR("param", fmt_str, None))
                        i += 1
                        if i < n and tokens[i].value == ",":
                            i += 1
                            if i < n:
                                arg = tokens[i].value
                                if not self.sym.find(arg) and arg != "flag":
                                    self.err(f"变量 '{arg}' 未定义", tokens[i].line, tokens[i].col)
                                self.ir.append(IR("param", arg, None))
                                self.ir.append(IR("call", "printf", None))
                                print(f" printf中间代码：param {fmt_str}, param {arg}, call printf")
                                i += 1
                        while i < n and tokens[i].value != ")":
                            i += 1
                        if i < n and tokens[i].value == ")":
                            i += 1
                if i < n and tokens[i].value == ";":
                    i += 1

            elif v == "flag":
                if not self.sym.find("flag") and not self.flag_error_reported:
                    self.err("变量 'flag' 未声明", line, col)
                    self.flag_error_reported = True
                if i+1 < n and tokens[i+1].value == "=":
                    i += 2
                    val = tokens[i].value
                    if val == "-" and i+1 < n:
                        val += tokens[i+1].value
                        i += 1
                    self.ir.append(IR("=", val, "flag"))
                    print(f" 赋值：flag = {val}")
                    i += 1
                if i < n and tokens[i].value == ";":
                    i += 1
            else:
                i += 1

        # 检查括号匹配 - 不自动补全，直接报错
        if self.brace_stack:
            open_line = self.brace_stack[-1]
            self.err("main() 函数体未闭合，缺少 '}'", open_line, 1)

        print("\n 语义分析结果 ")
        if self.errors:
            for l, c, m in self.errors:
                print(f"× 行{l}列{c}：{m}")
        else:
            print(" 未发现语义错误")

        print("\n符号表 ")
        all_vars = {**self.sym.globals, **self.sym.locals}
        for k, v in all_vars.items():
            print(f"变量：{k} → 类型：{v.type} 作用域：{v.scope}")

        print("\n= 中间代码（三元式）=")
        for line in self.ir:
            print(line)

        return self.ir, self.errors


# 测试代码（包含多个语义错误）
test_code = """
struct student{
    char* name;
    int num;
    int age;    
    float score;
};
void main(){
    int i, num_140 = 0;
    float sum = 0;
    
    struct student sts[2]={ 
        {"Li ping",5,18,145.0}, {"Wang ming",6,18,150.0}
    }; 
    int flag;
    if(sts[1].score<140)  flag=-1;
    else flag=1;    
    printf("%d ", flag);
}
"""

grammar_str = """
   PROGRAM -> EXT_DEF_LIST
EXT_DEF_LIST -> EXT_DEF EXT_DEF_LIST | ε
EXT_DEF ->  STRUCT_DEF | FUNC_OR_VAR
STRUCT_DEF -> struct id { FIELDS } STRUCT_NAME_OPT ; 
STRUCT_NAME_OPT -> id | ε
FIELDS -> TYPE id ARR_OPT ; FIELDS | ε
TYPE -> BASE_TYPE PTR_OPT | USER_TYPE PTR_OPT
BASE_TYPE -> int | char | float | void | double | long | short
USER_TYPE -> struct id 
PTR_OPT -> * PTR_OPT | ε
ARR_OPT -> [ num ] | ε
FUNC_OR_VAR -> TYPE id ( PARAMS ) BLOCK      
            | TYPE id VAR_TAIL               
VAR_TAIL -> ; | = INITIALIZER ; | [ num ] VAR_TAIL2
VAR_TAIL2 -> = INITIALIZER | ε
PARAMS -> PARAM PARAMS_TAIL | ε
PARAM -> TYPE id
PARAMS_TAIL -> , PARAM PARAMS_TAIL | ε
BLOCK -> { STMT_LIST }
STMT_LIST -> STMT STMT_LIST | ε
STMT -> printf ( STR_LIT PRINTF_ARGS_TAIL ) ;| BASE_TYPE PTR_OPT VAR_DECL_LIST ; | struct id PTR_OPT VAR_DECL_LIST ;| USER_TYPE PTR_OPT VAR_DECL_LIST ;| return EXPR_OPT ;| if ( COND_EXPR ) STMT_OR_BLOCK ELSE_PART | while ( COND_EXPR ) STMT_OR_BLOCK| do STMT_OR_BLOCK while ( COND_EXPR ) ; | for ( FOR_INIT ; COND_EXPR_OPT ; FOR_UPDATE ) STMT_OR_BLOCK | switch ( EXPR ) { CASE_LIST } | break ;| continue ;| id ID_STMT_TAIL 
STR_LIT -> str_lit
VAR_DECL_LIST -> id VAR_DECL_TAIL CONTINUE_VAR
CONTINUE_VAR -> , VAR_DECL_LIST | ε
STMT_OR_BLOCK -> { STMT_LIST } | SIMPLE_STMT
SIMPLE_STMT -> printf ( STR_LIT PRINTF_ARGS_TAIL ) ; | id ID_STMT_TAIL | return EXPR_OPT ; | break ; | continue ;
ELSE_PART -> else STMT_OR_BLOCK | ε
FOR_INIT -> BASE_TYPE id = EXPR | id = EXPR | ε
FOR_UPDATE -> id FOR_UPDATE_OP | ε
FOR_UPDATE_OP -> ++ | -- | += EXPR | -= EXPR | = EXPR
CASE_LIST -> CASE_ITEM CASE_LIST | ε
CASE_ITEM -> case num : STMT_LIST | default : STMT_LIST
COND_EXPR_OPT -> COND_EXPR | ε
EXPR_OPT -> EXPR | ε
ID_STMT_TAIL -> STMT_PRIME
STMT_PRIME -> = EXPR ;  | . id MEMBER_ACCESS_TAIL STMT_PRIME_TAIL | ( ARGS ) ;          | [ EXPR ] ASSIGN_TAIL  | ++ ; | -- ;  | += EXPR ;  | -= EXPR ;  | *= EXPR ; | /= EXPR ;
STMT_PRIME_TAIL -> = EXPR ; | ;
ASSIGN_TAIL -> = EXPR ; | ;
VAR_DECL_TAIL -> = INITIALIZER | [ num ] VAR_DECL_TAIL2 | ε
VAR_DECL_TAIL2 -> = INITIALIZER | ε
INITIALIZER -> { INIT_LIST } | EXPR | ε
INIT_LIST -> INITIALIZER INIT_LIST_TAIL | ε
INIT_LIST_TAIL -> , INITIALIZER INIT_LIST_TAIL | ε
PRINTF_ARGS_TAIL -> , EXPR | ε
	
MEMBER_ACCESS_TAIL -> [ EXPR ] | ε
ARGS -> EXPR ARGS_TAIL | ε
ARGS_TAIL -> , EXPR ARGS_TAIL | ε
COND_EXPR -> LOGIC_OR_EXPR
LOGIC_OR_EXPR -> LOGIC_AND_EXPR LOGIC_OR_TAIL
LOGIC_OR_TAIL -> || LOGIC_AND_EXPR LOGIC_OR_TAIL | ε
LOGIC_AND_EXPR -> COMPARE_EXPR LOGIC_AND_TAIL
LOGIC_AND_TAIL -> && COMPARE_EXPR LOGIC_AND_TAIL | ε
COMPARE_EXPR -> ARITH_EXPR COMPARE_TAIL
COMPARE_TAIL -> < ARITH_EXPR COMPARE_TAIL | > ARITH_EXPR COMPARE_TAIL | <= ARITH_EXPR COMPARE_TAIL | >= ARITH_EXPR COMPARE_TAIL | == ARITH_EXPR COMPARE_TAIL | != ARITH_EXPR COMPARE_TAIL | ε
ARITH_EXPR -> TERM ARITH_TAIL
ARITH_TAIL -> + TERM ARITH_TAIL | - TERM ARITH_TAIL | ε
TERM -> UNARY_EXPR TERM_TAIL
TERM_TAIL -> * UNARY_EXPR TERM_TAIL | / UNARY_EXPR TERM_TAIL | % UNARY_EXPR TERM_TAIL | ε
UNARY_EXPR -> ! UNARY_EXPR | - UNARY_EXPR | & UNARY_EXPR | ++ id | -- id | POSTFIX_EXPR
POSTFIX_EXPR -> PRIMARY POSTFIX_TAIL
POSTFIX_TAIL -> ++ POSTFIX_TAIL | -- POSTFIX_TAIL | [ EXPR ] POSTFIX_TAIL | . id POSTFIX_TAIL | ( ARGS ) POSTFIX_TAIL | ε
PRIMARY -> id | num | str_lit | ( COND_EXPR )
EXPR -> COND_EXPR
"""

def run_syntax_analysis(source_code: str):
    """运行词法+语法+语义分析，返回分析结果"""
    print("===== 1/4 词法分析 =====", flush=True)
    lexer = MainController()
    lexer.load_source(input_type="string", source_str=source_code)
    lexer.run_lexical_analysis()
    print("\n===== 2/4 语法分析 =====", flush=True)
    grammar = Grammar(grammar_str)
    parser = DynamicLL1Parser(grammar, lexer.result_handler.token_list)
    parser.run()
    print(" 语法分析完成！")
    print("\n===== 3/4 语义分析 & 中间代码 =====", flush=True)
    sa = SemanticAnalyzer(parser)
    sa.analyze()
    print("\n 运行完毕！")

def main():
    print("===== 1/4 词法分析 =====", flush=True)
    lexer = MainController()
    lexer.load_source(input_type="string", source_str=test_code)
    lexer.run_lexical_analysis()
    print("\n===== 2/4 语法分析 =====", flush=True)
    grammar = Grammar(grammar_str)
    parser = DynamicLL1Parser(grammar, lexer.result_handler.token_list)
    parser.run()
    print(" 语法分析完成！")
    print("\n===== 3/4 语义分析 & 中间代码 =====", flush=True)
    sa = SemanticAnalyzer(parser)
    sa.analyze()
    print("\n 运行完毕！")

if __name__ == "__main__":
    main()