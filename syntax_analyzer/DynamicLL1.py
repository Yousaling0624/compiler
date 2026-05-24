import sys
from collections import defaultdict

# 从Lexer.py导入词法分析器
from Lexer import MainController, Token

class Grammar:
    """
    文法类：解析自定义文法字符串，计算FIRST集/FOLLOW集，构建LL(1)预测分析表
    核心属性：
        productions: defaultdict - 产生式规则（键：非终结符，值：右部候选式列表）
        non_terminals: set - 非终结符集合
        terminals: set - 终结符集合（含$）
        start_symbol: str - 文法起始符号
        first: defaultdict - 各符号的FIRST集
        follow: defaultdict - 各非终结符的FOLLOW集
        table: defaultdict - LL(1)预测分析表（table[非终结符][终结符] = 产生式右部）
    """
    def __init__(self, grammar_str):
        # 初始化产生式、非终结符、终结符、起始符号
        self.productions = defaultdict(list)
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None

        # 1. 解析输入的文法字符串为结构化产生式
        self._parse_grammar(grammar_str)

        # 2. 初始化FIRST/FOLLOW集和预测分析表
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.table = defaultdict(dict)

        # 3. 执行LL(1)核心算法
        print(">> 正在计算 FIRST 集...")
        self._compute_first()
        print(">> 正在计算 FOLLOW 集...")
        self._compute_follow()
        print(">> 正在构建预测分析表...")
        self._build_table()


        self._print_debug_info()

    def _parse_grammar(self, grammar_str):
        """
        解析文法字符串为结构化的产生式规则
        文法格式要求：每行一个产生式，格式为"非终结符 -> 候选式1 | 候选式2 | ..."
        空串用ε或EPSILON表示，候选式内符号用空格分隔
        :param grammar_str: 自定义文法字符串
        """
        for line in grammar_str.strip().split('\n'):
            line = line.strip()
            if not line:  # 跳过空行
                continue

            # 跳过注释行
            if line.startswith('#'):
                continue

            try:
                # 拆分产生式左部（LHS）和右部（RHS）
                lhs, rhs_list = line.split('->')
            except ValueError:  # 格式错误的行，跳过
                continue

            lhs = lhs.strip()
            # 第一个非终结符作为起始符号
            if self.start_symbol is None:
                self.start_symbol = lhs

            # 左部加入非终结符集合
            self.non_terminals.add(lhs)

            # 拆分右部的多个候选式（|分隔）
            alternatives = rhs_list.split('|')
            for alt in alternatives:
                symbols = alt.strip().split()
                # 处理空串候选式（ε/EPSILON）
                if symbols == ['ε'] or symbols == ['EPSILON']:
                    self.productions[lhs].append([])
                else:
                    self.productions[lhs].append(symbols)
                    # 候选式中的符号加入终结符候选集（后续去重）
                    for s in symbols:
                        self.terminals.add(s)

        # 修正终结符集合：移除非终结符，添加结束符$
        self.terminals = self.terminals - self.non_terminals
        self.terminals.add('$')

    def _compute_first(self):
        """
        计算所有符号的FIRST集（不动点迭代算法）
        FIRST集定义：符号α可以推导出的所有以终结符开头的集合，若α能推导出ε则包含ε
        """
        # 初始化：终结符的FIRST集是自身
        for term in self.terminals:
            if term != '$':  # $是结束符，不参与FIRST计算
                self.first[term].add(term)

        changed = True
        # 迭代直到FIRST集不再变化
        while changed:
            changed = False
            # 遍历每个产生式
            for head, bodies in self.productions.items():
                for body in bodies:
                    # 情况1：产生式右部为空（ε）
                    if not body:
                        if 'ε' not in self.first[head]:
                            self.first[head].add('ε')
                            changed = True
                        continue

                    # 情况2：产生式右部非空，逐符号计算
                    all_derive_epsilon = True  # 标记是否所有符号都能推导出ε
                    for symbol in body:
                        # 子情况2.1：符号是终结符 → 加入FIRST(head)
                        if symbol in self.terminals:
                            if symbol not in self.first[head]:
                                self.first[head].add(symbol)
                                changed = True
                            all_derive_epsilon = False
                            break

                        # 子情况2.2：符号是非终结符 → 合并其FIRST集（排除ε）到FIRST(head)
                        if symbol in self.non_terminals:
                            trait = self.first[symbol]
                            for t in trait:
                                if t != 'ε' and t not in self.first[head]:
                                    self.first[head].add(t)
                                    changed = True

                            # 若当前符号不能推导出ε，终止遍历
                            if 'ε' not in trait:
                                all_derive_epsilon = False
                                break

                    # 若所有符号都能推导出ε → FIRST(head)加入ε
                    if all_derive_epsilon:
                        if 'ε' not in self.first[head]:
                            self.first[head].add('ε')
                            changed = True

    def _compute_follow(self):
        """
        计算所有非终结符的FOLLOW集（不动点迭代算法）
        FOLLOW集定义：非终结符A的FOLLOW集是所有出现在句型中A之后的终结符，起始符号包含$
        """
        # 初始化：起始符号的FOLLOW集加入结束符$
        self.follow[self.start_symbol].add('$')

        changed = True
        # 迭代直到FOLLOW集不再变化
        while changed:
            changed = False
            # 遍历每个产生式
            for head, bodies in self.productions.items():
                for body in bodies:
                    # 遍历产生式右部的每个符号
                    for i, symbol in enumerate(body):
                        # 仅处理非终结符
                        if symbol not in self.non_terminals:
                            continue

                        # 计算符号后剩余部分的FIRST集（rest_first）
                        rest = body[i + 1:]  # 符号后的剩余符号序列
                        rest_first = set()
                        all_rest_epsilon = True  # 剩余部分是否能推导出ε

                        if rest:  # 剩余部分非空
                            for r_sym in rest:
                                # 子情况1：剩余符号是终结符 → 加入rest_first
                                if r_sym in self.terminals:
                                    rest_first.add(r_sym)
                                    all_rest_epsilon = False
                                    break
                                # 子情况2：剩余符号是非终结符 → 合并其FIRST集（排除ε）到rest_first
                                elif r_sym in self.non_terminals:
                                    rest_first.update(self.first[r_sym] - {'ε'})
                                    if 'ε' not in self.first[r_sym]:
                                        all_rest_epsilon = False
                                        break

                        # 步骤1：将rest_first加入FOLLOW(symbol)
                        for f in rest_first:
                            if f not in self.follow[symbol]:
                                self.follow[symbol].add(f)
                                changed = True

                        # 步骤2：若剩余部分能推导出ε → 将FOLLOW(head)加入FOLLOW(symbol)
                        if all_rest_epsilon:
                            for f in self.follow[head]:
                                if f not in self.follow[symbol]:
                                    self.follow[symbol].add(f)
                                    changed = True

    def _build_table(self):
        """
        构建LL(1)预测分析表
        表项规则：
            1. 对产生式A→α，若终结符a∈FIRST(α) → table[A][a] = α
            2. 若ε∈FIRST(α)且终结符b∈FOLLOW(A) → table[A][b] = α
        """
        # 遍历每个产生式
        for head, bodies in self.productions.items():
            for body in bodies:
                prod_first = set()  # 产生式右部的FIRST集
                all_epsilon = True  # 产生式右部是否能推导出ε

                if body:  # 产生式右部非空
                    for sym in body:
                        # 子情况1：符号是终结符 → 加入prod_first
                        if sym in self.terminals:
                            prod_first.add(sym)
                            all_epsilon = False
                            break
                        # 子情况2：符号是非终结符 → 合并其FIRST集（排除ε）到prod_first
                        elif sym in self.non_terminals:
                            prod_first.update(self.first[sym] - {'ε'})
                            if 'ε' not in self.first[sym]:
                                all_epsilon = False
                                break

                # 规则1：prod_first中的终结符对应表项
                for term in prod_first:
                    if term not in self.table[head]:
                        self.table[head][term] = body

                # 规则2：若右部能推导出ε → FOLLOW(head)中的终结符对应表项
                if all_epsilon:
                    for term in self.follow[head]:
                        if term not in self.table[head]:
                            self.table[head][term] = body

    def get_production(self, non_terminal, terminal):
        """
        获取预测分析表中的产生式
        :param non_terminal: 非终结符
        :param terminal: 终结符
        :return: 产生式右部（列表），无匹配则返回None
        """
        return self.table[non_terminal].get(terminal)

    def _print_debug_info(self):
        """打印调试信息：关键非终结符的FIRST/FOLLOW集和分析表"""
        print("\n=== 调试信息：关键FIRST/FOLLOW集 ===")
        key_non_terms = ["PROGRAM", "EXT_DEF_LIST", "EXT_DEF", "MACRO", "TYPEDEF_STRUCT", "STRUCT_DEF", "FUNC_OR_VAR", "TYPE", "BASE_TYPE", "USER_TYPE", "PTR_OPT", "STMT", "STMT_PRIME"]
        for nt in key_non_terms:
            if nt in self.first:
                print(f"FIRST({nt}): {sorted(self.first[nt])}")
            if nt in self.follow:
                print(f"FOLLOW({nt}): {sorted(self.follow[nt])}")
        
        print("\n=== 调试信息：关键分析表项 ===")
        # 检查EXT_DEF_LIST对#的匹配
        print(f"table[EXT_DEF_LIST][#]: {self.table.get('EXT_DEF_LIST', {}).get('#')}")
        # 检查EXT_DEF对struct的匹配
        print(f"table[EXT_DEF][struct]: {self.table.get('EXT_DEF', {}).get('struct')}")
        # 检查PTR_OPT对*的匹配
        print(f"table[PTR_OPT][*]: {self.table.get('PTR_OPT', {}).get('*')}")
        # 检查VAL_TAIL对.的匹配
        print(f"table[VAL_TAIL][.]: {self.table.get('VAL_TAIL', {}).get('.')}")
        # 检查STMT对id的匹配
        print(f"table[STMT][id]: {self.table.get('STMT', {}).get('id')}")
        # 检查STMT_PRIME对.的匹配
        print(f"table[STMT_PRIME][.]: {self.table.get('STMT_PRIME', {}).get('.')}")

class DynamicLL1Parser:
    """
    LL(1)语法分析器：基于Grammar生成的预测分析表，对Token列表进行自顶向下语法分析
    核心流程：利用分析栈，匹配输入Token，查表推导非终结符，直到栈空且输入耗尽
    """
    def __init__(self, grammar: Grammar, token_list: list):
        """
        初始化分析器
        :param grammar: 已构建好的Grammar实例
        :param token_list: Lexer产生的Token列表
        """
        self.grammar = grammar
        # 过滤EOF Token，添加结束符$对应的Token
        self.tokens = [t for t in token_list if t.value != "END_OF_FILE"]
        self.tokens.append(Token("EOF", "$", 0, 0))
        self.pos = 0                # 当前处理的Token索引
        self.stack = ["$", grammar.start_symbol]  # 分析栈（初始：$ + 起始符号）

    def get_terminal(self, token):
        """
        核心映射方法：将Token对象转换为文法中定义的终结符
        适配 lexer.py 的 Token 类型格式（如"关键字 - int"、"界符 ("等）
        :param token: Token对象
        :return: 文法中的终结符字符串
        """
        if token.value == "$":
            return "$"
        
        # 1. 双字符运算符优先映射
        double_ops = {"++", "--", "+=", "-=", "*=", "/=", "==", "!=", "<=", ">=", "&&", "||"}
        if token.value in double_ops:
            return token.value

        # 2. 单字符运算符和界符映射
        special_chars = {"#", "<", ">", "{", "}", "(", ")", ";", ",", "=", "+", "-", "*", "/", "[", "]", ".", "%", "!", ":", "&", "|"}
        if token.value in special_chars:
            return token.value

        # 3. 类型优先映射：常量类Token（适配lexer.py的多种常量类型）
        if "字符串常量" in token.type:
            return "str_lit"
        if "字符常量" in token.type:
            return "str_lit"
        # 适配lexer.py的各种数值常量类型
        if any(num_type in token.type for num_type in ["整数常量", "浮点常量", "十进制", "八进制", "十六进制", "二进制"]):
            return "num"

        # 4. 关键字映射：适配lexer.py的"关键字 - xxx"格式
        keywords = {
            "include", "typedef", "struct", "int", "char", "float", "void", "return",
            "if", "else", "for", "while", "do", "switch", "case", "default",
            "break", "continue", "double", "long", "short", "printf"
        }
        if token.value in keywords:
            return token.value
        # 兼容"关键字 - xxx"格式
        if "关键字" in token.type:
            return token.value

        # 5. 标识符映射：所有标识符Token（含main）映射为id
        if "标识符" in token.type:
            return "id"

        # 兜底：返回Token原始值（确保不丢失信息）
        return token.value

    def run(self):
        """执行LL(1)语法分析的核心方法，输出分析过程和结果"""
        # 打印分析表头
        print(f"\n{'步骤':<5} | {'分析栈':<60} | {'当前符号':<10} | {'动作'}")
        print("-" * 120)

        step = 0  # 分析步骤计数器
        while self.stack:
            step += 1
            top = self.stack[-1]  # 栈顶符号

            # 边界检查：输入Token耗尽
            if self.pos >= len(self.tokens): 
                print(f"Error: 步骤{step} - 输入意外结束，剩余栈：{self.stack}")
                return

            # 获取当前Token对应的终结符
            curr_token = self.tokens[self.pos]
            term = self.get_terminal(curr_token)

            # 情况1：栈顶是终结符（含$）
            if top in self.grammar.terminals or top == "$":
                # 子情况1.1：栈顶与当前终结符匹配 → 出栈，Token指针后移
                if top == term:
                    # 栈过长时仅展示最后5个元素，便于查看
                    stack_disp = str(self.stack[-5:]) if len(self.stack) > 5 else str(self.stack)
                    print(f"{step:<5} | {stack_disp:<60} | {term:<10} | 匹配 '{term}'")
                    self.stack.pop()
                    self.pos += 1
                # 子情况1.2：不匹配 → 语法错误
                else:
                    print(f"Error: 步骤{step} - 期待 '{top}' 但遇到 '{term}' (Token: {curr_token.value})")
                    # 打印上下文帮助排查
                    print(f"  上下文：当前栈={self.stack}, 当前Token位置={self.pos}, Token列表前10个={self.tokens[:10]}")
                    return

            # 情况3：栈顶是非终结符 → 查表推导
            elif top in self.grammar.non_terminals:
                # 获取预测分析表中的产生式
                prod = self.grammar.get_production(top, term)
                if prod is None:
                    # 无匹配产生式 → 语法错误
                    print(f"Error: 步骤{step} - 非终结符 '{top}' 无法接受输入 '{term}' (Token: {curr_token.value})")
                    # 打印可用的预测项帮助排查
                    available_terms = list(self.grammar.table.get(top, {}).keys())
                    print(f"  非终结符 {top} 可匹配的终结符：{available_terms}")
                    return

                # 出栈非终结符，逆序入栈产生式右部（ε则不入栈）
                self.stack.pop()
                for symbol in reversed(prod):
                    self.stack.append(symbol)

                # 格式化输出推导动作
                arrow = f"{top} -> {' '.join(prod) if prod else 'ε'}"
                stack_disp = str(self.stack[-5:]) if len(self.stack) > 5 else str(self.stack)
                print(f"{step:<5} | {stack_disp:<60} | {term:<10} | {arrow}")

            # 未知符号处理
            else:
                print(f"Error: 步骤{step} - 栈顶出现未知符号 '{top}'")
                return

        # 循环正常结束 → 语法分析成功
        print("\nSUCCESS: 分析成功完成！")

# 测试代码：单独运行DynamicLL1.py时执行
if __name__ == "__main__":

    # === C语言子集文法定义（修改后的版本）===
    c_grammar_str = """
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

# ========== 函数和变量声明 ==========
FUNC_OR_VAR -> TYPE id ( PARAMS ) BLOCK      
            | TYPE id VAR_TAIL               

VAR_TAIL -> ; | = INITIALIZER ; | [ num ] VAR_TAIL2
VAR_TAIL2 -> = INITIALIZER | ε

PARAMS -> PARAM PARAMS_TAIL | ε
PARAM -> TYPE id
PARAMS_TAIL -> , PARAM PARAMS_TAIL | ε

BLOCK -> { STMT_LIST }
STMT_LIST -> STMT STMT_LIST | ε

# ========== 修改 STMT 规则 ==========
STMT -> printf ( STR_LIT , EXPR ) ;| BASE_TYPE PTR_OPT VAR_DECL_LIST ; | struct id PTR_OPT VAR_DECL_LIST ;| USER_TYPE PTR_OPT VAR_DECL_LIST ;| return EXPR_OPT ;| if ( COND_EXPR ) STMT_OR_BLOCK ELSE_PART | while ( COND_EXPR ) STMT_OR_BLOCK| do STMT_OR_BLOCK while ( COND_EXPR ) ; | for ( FOR_INIT ; COND_EXPR_OPT ; FOR_UPDATE ) STMT_OR_BLOCK | switch ( EXPR ) { CASE_LIST } | break ;| continue ;| id ID_STMT_TAIL 

STR_LIT -> str_lit

VAR_DECL_LIST -> id VAR_DECL_TAIL CONTINUE_VAR
CONTINUE_VAR -> , VAR_DECL_LIST | ε

STMT_OR_BLOCK -> { STMT_LIST } | SIMPLE_STMT

SIMPLE_STMT -> id ID_STMT_TAIL | return EXPR_OPT ; | break ; | continue ;

ELSE_PART -> else STMT_OR_BLOCK | ε

FOR_INIT -> BASE_TYPE id = EXPR | id = EXPR | ε
FOR_UPDATE -> id FOR_UPDATE_OP | ε
FOR_UPDATE_OP -> ++ | -- | += EXPR | -= EXPR | = EXPR

CASE_LIST -> CASE_ITEM CASE_LIST | ε
CASE_ITEM -> case num : STMT_LIST | default : STMT_LIST

COND_EXPR_OPT -> COND_EXPR | ε
EXPR_OPT -> EXPR | ε

ID_STMT_TAIL -> STMT_PRIME


STMT_PRIME -> = EXPR ;  | . id MEMBER_ACCESS_TAIL STMT_PRIME_TAIL | ( ARGS ) ;          # 函数调用 | [ EXPR ] ASSIGN_TAIL  | ++ ; | -- ;  | += EXPR ;  | -= EXPR ;  | *= EXPR ; | /= EXPR ;

STMT_PRIME_TAIL -> = EXPR ; | ;
ASSIGN_TAIL -> = EXPR ; | ;

VAR_DECL_TAIL -> = INITIALIZER | [ num ] VAR_DECL_TAIL2 | ε
VAR_DECL_TAIL2 -> = INITIALIZER | ε

INITIALIZER -> { INIT_LIST } | EXPR | ε
INIT_LIST -> INITIALIZER INIT_LIST_TAIL | ε
INIT_LIST_TAIL -> , INITIALIZER INIT_LIST_TAIL | ε

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

UNARY_EXPR -> ! UNARY_EXPR | - UNARY_EXPR | ++ id | -- id | POSTFIX_EXPR

POSTFIX_EXPR -> PRIMARY POSTFIX_TAIL
POSTFIX_TAIL -> ++ POSTFIX_TAIL | -- POSTFIX_TAIL | [ EXPR ] POSTFIX_TAIL | . id POSTFIX_TAIL | ( ARGS ) POSTFIX_TAIL | ε

PRIMARY -> id | num | str_lit | ( COND_EXPR )

EXPR -> COND_EXPR
    """

    print(">>> 1. 初始化文法与构建分析表 <<<")
    grammar = Grammar(c_grammar_str)

    print("\n>>> 2. 启动词法分析 <<<")

   
    test_code = """

     struct student{
        char* name; //姓名
        int num;   //学号
        int age;   //年龄
        float score;  //成绩
    }
    void main(){
        int i, num_140 = 0;
        float sum = 0;
       struct student sts[2] = {
        {"Li ping",5,18,145.0}
        ,{"Wang ming",6,18,150.0}};
        if(sts[1].score < 140) 
        flag = -1;
        else flag=1;
        printf("%d", flag);

    """

    # 执行词法分析
    lexer = MainController()
    lexer.load_source(input_type="string", source_str=test_code)
    lexer.run_lexical_analysis()

    # 打印词法分析结果（便于调试）
    print("\n=== 词法分析结果（Token列表）===")
    for i, token in enumerate(lexer.result_handler.token_list[:30]):  # 打印前30个Token
        print(f"{i}: {token}")

    print("\n>>> 3. 启动动态 LL(1) 语法分析 <<<")
    # 词法分析无错误时，执行语法分析
    if not lexer.result_handler.error_flag:
        parser = DynamicLL1Parser(grammar, lexer.result_handler.token_list)
        parser.run()
    else:
        print("词法分析发现错误，跳过语法分析。")