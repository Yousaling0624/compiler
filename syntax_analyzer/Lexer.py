class Token:
    def __init__(self, token_type: str, token_value: str, line: int, col: int):
        self.type = token_type
        self.value = token_value
        self.line = line
        self.col = col

    def __str__(self):
        return f"Token(type='{self.type}', value='{self.value}', line={self.line}, col={self.col})"

    def __repr__(self):
        return self.__str__()


class ResultOutputHandler:
    def __init__(self):
        self.token_list = []
        self.error_logs = []
        self.error_flag = False

    def add_token(self, token: Token):
        self.token_list.append(token)

    def record_error(self, error_type: str, desc: str, line: int, col: int):
        self.error_logs.append({
            "error_type": error_type,
            "description": desc,
            "line": line,
            "col": col
        })
        self.error_flag = True

    def final_output(self):
        print("=" * 60)
        print("词法分析结果 - Token列表")
        print("=" * 60)
        eof_line = self.token_list[-1].line if self.token_list else 1
        self.token_list.append(Token("结束标记", "END_OF_FILE", eof_line, 1))
        for idx, token in enumerate(self.token_list, 1):
            print(f"{idx:3d}. {token}")

        print("\n" + "=" * 60)
        if self.error_flag:
            print("词法错误汇总")
            print("=" * 60)
            for idx, error in enumerate(self.error_logs, 1):
                print(
                    f"{idx}. 类型：{error['error_type']:8s} | 位置：行{error['line']}列{error['col']} | 描述：{error['description']}")
        else:
            print("词法分析结果:无任何词法错误")
        print("=" * 60)


class KeywordSymbolRecognizer:
    def __init__(self):
        self.KEYWORDS = {
            "int", "void", "float", "char", "if", "else", "while", "return",
            "auto", "break", "case", "const", "continue", "default", "do",
            "double", "enum", "extern", "for", "goto", "long", "short",
            "signed", "sizeof", "static", "struct", "switch", "typedef",
            "union", "unsigned", "register"
        }
        self.DOUBLE_SYMBOLS = {
            "++": "运算符++", "--": "运算符--", "&&": "运算符&&", "||": "运算符||",
            "==": "运算符==", "!=": "运算符!=", "<=": "运算符<=", ">=": "运算符>=",
            "<<": "运算符<<", ">>": "运算符>>", "+=": "运算符+=", "-=": "运算符-=",
            "*=": "运算符*=", "/=": "运算符/=", "%=": "运算符%=", "->": "界符->"
        }
        self.SINGLE_SYMBOLS = {
            "+": "运算符+", "-": "运算符-", "*": "运算符*", "/": "运算符/",
            "=": "运算符=", "<": "运算符<", ">": "运算符>", "!": "运算符!",
            "%": "运算符%", "&": "运算符&", "|": "运算符|", "^": "运算符^",
            "~": "运算符~", "?": "运算符?", ":": "运算符:",
            "(": "界符 (", ")": "界符 )", "{": "界符 {", "}": "界符 }",
            ",": "界符 ,", ";": "界符 ;", "[": "界符 [", "]": "界符 ]",
            ".": "界符 .", "#": "界符 #"
        }

    def recognize(self, source_code: str, pos: int, line: int, col: int) -> tuple[Token | None, int, int, int]:
        current_pos, current_line, current_col = pos, line, col
        n = len(source_code)

        if current_pos < n and source_code[current_pos].isalpha():
            keyword_end = current_pos
            while keyword_end < n and source_code[keyword_end].isalpha():
                keyword_end += 1
            candidate_str = source_code[current_pos:keyword_end]
            if (candidate_str in self.KEYWORDS and
                    (keyword_end >= n or not (source_code[keyword_end].isalnum() or source_code[keyword_end] == "_"))):
                return (
                    Token(f"关键字 - {candidate_str}", candidate_str, line, col),
                    keyword_end, current_line, col + (keyword_end - current_pos)
                )
            else:
                return None, pos, line, col

        if current_pos + 1 < n:
            double_candidate = source_code[current_pos:current_pos + 2]
            if double_candidate in self.DOUBLE_SYMBOLS:
                return (
                    Token(self.DOUBLE_SYMBOLS[double_candidate], double_candidate, line, col),
                    current_pos + 2, current_line, col + 2
                )

        if current_pos < n and source_code[current_pos] in self.SINGLE_SYMBOLS:
            char = source_code[current_pos]
            return (
                Token(self.SINGLE_SYMBOLS[char], char, line, col),
                current_pos + 1, current_line, col + 1
            )
        return None, pos, line, col


class ConstIdRecognizer:
    def __init__(self):
        self.DELIMITERS = {' ', '\t', '\n', '=', ';', '(', ')', '{', '}', ',',
                           '+', '-', '*', '/', '<', '>', '!', '?', ':', '[', ']', '.', '%'}
        self.HEX_CHARS = set('0123456789abcdefABCDEF')
        self.OCT_CHARS = set('01234567')
        self.BIN_CHARS = set('01')
        self.FLOAT_SUFFIXES = {'f', 'F', 'l', 'L'}
        self.DOUBLE_FLOAT_SUFFIXES = {'lf', 'LF'}
        self.EXPONENT_CHARS = {'e', 'E'}
        self.SIGN_CHARS = {'+', '-'}
        self.INTEGER_SUFFIXES = {
            'ull', 'ULL', 'llu', 'LLU', 'Ull', 'uLL', 'UlL', 'uLl',
            'll', 'LL', 'ul', 'UL', 'lu', 'LU', 'uL', 'Ul',
            'u', 'U', 'l', 'L'
        }
        # 新增：常见标识符笔误映射
        self.ID_TYPO_MAP = {
            "1i": "Li",
            "2a": "Aa",
            "3b": "Bb",
            "0n": "On"
        }

    def recognize(self, source_code: str, pos: int, line: int, col: int) -> tuple[Token | None, int, int, int]:
        current_pos, current_line, current_col = pos, line, col
        n = len(source_code)

        # 新增：检测数字开头的非法标识符（如1i、2a）
        if current_pos < n and source_code[current_pos].isdigit():
            illegal_end = current_pos
            while illegal_end < n and (source_code[illegal_end].isalnum() or source_code[illegal_end] == "_"):
                illegal_end += 1
            illegal_str = source_code[current_pos:illegal_end]
            if len(illegal_str) > 1 and any(c.isalpha() for c in illegal_str):
                typo_suggest = self.ID_TYPO_MAP.get(illegal_str, None)
                if typo_suggest:
                    desc = f"非法标识符 '{illegal_str}'（数字开头，不符合C语言标识规则），疑似笔误：建议改为 '{typo_suggest}'"
                else:
                    desc = f"非法标识符 '{illegal_str}'（数字开头，不符合C语言标识规则，标识符需以字母/下划线开头）"
                # 记录错误（需通过MainController传递result_handler）
                if hasattr(self, 'result_handler'):
                    self.result_handler.record_error("非法标识符", desc, line, col)
                current_col = col + (illegal_end - current_pos)
                return None, illegal_end, current_line, current_col

        # 0. 字符串常量（原有逻辑）
        if current_pos < n and source_code[current_pos] == '"':
            start_col = col
            current_pos += 1
            current_col += 1
            while current_pos < n and source_code[current_pos] != '"':
                if source_code[current_pos] == '\\':
                    current_pos += 1
                    current_col += 1
                    if current_pos < n:
                        current_pos += 1
                        current_col += 1
                elif source_code[current_pos] == '\n':
                    current_line += 1
                    current_col = 1
                    current_pos += 1
                else:
                    current_col += 1
                    current_pos += 1
            if current_pos >= n:
                return None, pos, line, col
            else:
                str_content = source_code[pos + 1:current_pos]
                current_pos += 1
                current_col += 1
                return (
                    Token("字符串常量", f'"{str_content}"', line, start_col),
                    current_pos, current_line, current_col
                )

        # 1. 字符常量（原有逻辑）
        if current_pos < n and source_code[current_pos] == "'":
            start_col = col
            current_pos += 1
            current_col += 1
            if current_pos >= n:
                return None, pos, line, col
            if source_code[current_pos] == '\\':
                current_pos += 1
                current_col += 1
                if current_pos < n:
                    current_pos += 1
                    current_col += 1
            else:
                current_pos += 1
                current_col += 1
            if current_pos >= n or source_code[current_pos] != "'":
                return None, pos, line, col
            char_content = source_code[pos:current_pos + 1]
            current_pos += 1
            current_col += 1
            return (
                Token("字符常量", char_content, line, start_col),
                current_pos, current_line, current_col
            )

        # 2. 非十进制整数（原有逻辑）
        if current_pos < n and source_code[current_pos].isdigit():
            start_pos = current_pos
            start_line, start_col = line, col
            # 2.1 二进制（0b/0B）
            if (current_pos + 1 < n and
                    source_code[current_pos] == '0' and
                    source_code[current_pos + 1].lower() == 'b'):
                current_pos += 2
                while current_pos < n and source_code[current_pos] in self.BIN_CHARS:
                    current_pos += 1
                int_suffix = self._get_integer_suffix(source_code, current_pos, n)
                current_pos += len(int_suffix)
                if current_pos > start_pos + 2:
                    bin_str = source_code[start_pos:current_pos]
                    if current_pos >= n or not source_code[current_pos].isalnum():
                        return (
                            Token("二进制整数常量", bin_str, start_line, start_col),
                            current_pos, current_line, start_col + (current_pos - start_pos)
                        )
                return None, pos, line, col
            # 2.2 十六进制（0x/0X）
            if (current_pos + 1 < n and
                    source_code[current_pos] == '0' and
                    source_code[current_pos + 1].lower() == 'x'):
                current_pos += 2
                while current_pos < n and source_code[current_pos] in self.HEX_CHARS:
                    current_pos += 1
                int_suffix = self._get_integer_suffix(source_code, current_pos, n)
                current_pos += len(int_suffix)
                if current_pos > start_pos + 2:
                    hex_str = source_code[start_pos:current_pos]
                    if current_pos >= n or not source_code[current_pos].isalnum():
                        return (
                            Token("十六进制整数常量", hex_str, start_line, start_col),
                            current_pos, current_line, start_col + (current_pos - start_pos)
                        )
                return None, pos, line, col
            # 2.3 八进制（0开头+0-7）
            if source_code[current_pos] == '0' and current_pos + 1 <= n:
                current_pos += 1
                has_oct_digits = False
                while current_pos < n and source_code[current_pos] in self.OCT_CHARS:
                    has_oct_digits = True
                    current_pos += 1
                int_suffix = self._get_integer_suffix(source_code, current_pos, n)
                current_pos += len(int_suffix)
                oct_str = source_code[start_pos:current_pos]
                if (current_pos >= n or not source_code[current_pos].isalnum()) and not (
                        current_pos < n and source_code[current_pos] == '.'):
                    return (
                        Token("八进制整数常量", oct_str, start_line, start_col),
                        current_pos, current_line, start_col + (current_pos - start_pos)
                    )
                return None, pos, line, col

        # 3. 浮点数和十进制整数（原有逻辑）
        if current_pos < n and (source_code[current_pos].isdigit() or
                                (current_pos + 1 < n and source_code[current_pos] == '.' and source_code[
                                    current_pos + 1].isdigit())):
            start_pos = current_pos
            has_digit = False
            has_dot = False
            has_exponent = False
            while current_pos < n and source_code[current_pos].isdigit():
                has_digit = True
                current_pos += 1
            if current_pos < n and source_code[current_pos] == '.':
                has_dot = True
                current_pos += 1
                while current_pos < n and source_code[current_pos].isdigit():
                    has_digit = True
                    current_pos += 1
                if not has_digit:
                    if start_pos < current_pos - 1:
                        has_digit = True
            if current_pos < n and source_code[current_pos].lower() == 'e':
                has_exponent = True
                current_pos += 1
                if current_pos < n and source_code[current_pos] in self.SIGN_CHARS:
                    current_pos += 1
                exponent_has_digit = False
                while current_pos < n and source_code[current_pos].isdigit():
                    exponent_has_digit = True
                    current_pos += 1
                if not exponent_has_digit:
                    current_pos = start_pos
                    has_exponent = False
            float_suffix = ""
            if has_dot or has_exponent:
                if current_pos + 1 < n:
                    candidate_2 = source_code[current_pos:current_pos + 2]
                    if candidate_2 in self.DOUBLE_FLOAT_SUFFIXES:
                        float_suffix = candidate_2
                        current_pos += 2
                if not float_suffix and current_pos < n:
                    candidate_1 = source_code[current_pos]
                    if candidate_1 in self.FLOAT_SUFFIXES:
                        float_suffix = candidate_1
                        current_pos += 1
            if has_digit:
                if has_dot or has_exponent:
                    const_str = source_code[start_pos:current_pos]
                    if current_pos >= n or (source_code[current_pos] in self.DELIMITERS or not source_code[current_pos].isalnum()):
                        return (
                            Token("浮点常量", const_str, line, col),
                            current_pos, current_line, col + (current_pos - start_pos)
                        )
                else:
                    int_suffix = self._get_integer_suffix(source_code, current_pos, n)
                    current_pos += len(int_suffix)
                    const_str = source_code[start_pos:current_pos]
                    if (const_str == "0" or not const_str.startswith("0")) and \
                       (current_pos >= n or not source_code[current_pos].isalnum()):
                        return (
                            Token("十进制整数常量", const_str, line, col),
                            current_pos, current_line, col + (current_pos - start_pos)
                        )
            return None, pos, line, col

        # 4. 标识符识别（原有逻辑）
        if current_pos < n and (source_code[current_pos].isalpha() or source_code[current_pos] == "_"):
            id_end = current_pos
            while id_end < n and (source_code[id_end].isalnum() or source_code[id_end] == "_"):
                id_end += 1
            id_str = source_code[current_pos:id_end]
            if id_end >= n or source_code[id_end] in self.DELIMITERS:
                return (
                    Token("标识符", id_str, line, col),
                    id_end, current_line, col + (id_end - current_pos)
                )

        return None, pos, line, col

    def _get_integer_suffix(self, source: str, pos: int, n: int) -> str:
        if pos + 2 < n:
            candidate_3 = source[pos:pos + 3]
            if candidate_3 in self.INTEGER_SUFFIXES:
                return candidate_3
        if pos + 1 < n:
            candidate_2 = source[pos:pos + 2]
            if candidate_2 in self.INTEGER_SUFFIXES:
                return candidate_2
        if pos < n:
            candidate_1 = source[pos]
            if candidate_1 in self.INTEGER_SUFFIXES:
                return candidate_1
        return ""


class MainController:
    def __init__(self):
        self.source_code = ""
        self.pos = 0
        self.line = 1
        self.col = 1
        self.result_handler = ResultOutputHandler()
        self.key_symbol_module = KeywordSymbolRecognizer()
        self.const_id_module = ConstIdRecognizer()
        # 新增：将result_handler传递给ConstIdRecognizer，用于记录错误
        self.const_id_module.result_handler = self.result_handler

    def load_source(self, input_type: str = "string", source_str: str = None):
        if input_type == "string" and source_str:
            self.source_code = source_str
            print("成功加载源代码字符串")
        else:
            print("源代码加载失败")

    def skip_whitespace_and_comment(self):
        while self.pos < len(self.source_code):
            current_char = self.source_code[self.pos]
            if current_char in [' ', '\t']:
                self.pos += 1
                self.col += 1 if current_char == ' ' else 4
                continue
            elif current_char == '\n':
                self.pos += 1
                self.line += 1
                self.col = 1
                continue
            # 多行注释 /* ... */
            if (current_char == '/' and
                    self.pos + 1 < len(self.source_code) and
                    self.source_code[self.pos + 1] == '*'):
                comment_start_line, comment_start_col = self.line, self.col
                self.pos += 2
                self.col += 2
                while self.pos < len(self.source_code):
                    if (self.source_code[self.pos] == '*' and
                            self.pos + 1 < len(self.source_code) and
                            self.source_code[self.pos + 1] == '/'):
                        self.pos += 2
                        self.col += 2
                        break
                    elif self.source_code[self.pos] == '\n':
                        self.pos += 1
                        self.line += 1
                        self.col = 1
                    else:
                        self.pos += 1
                        self.col += 1
                else:
                    self.result_handler.record_error(
                        "未闭合注释", "多行注释缺少'*/'闭合",
                        comment_start_line, comment_start_col
                    )
                continue
            # 单行注释 // ...
            if (current_char == '/' and
                    self.pos + 1 < len(self.source_code) and
                    self.source_code[self.pos + 1] == '/'):
                while self.pos < len(self.source_code) and self.source_code[self.pos] != '\n':
                    self.pos += 1
                    self.col += 1
                continue
            break

    def run_lexical_analysis(self):
        while self.pos < len(self.source_code):
            self.skip_whitespace_and_comment()
            if self.pos >= len(self.source_code):
                break
            start_pos, start_line, start_col = self.pos, self.line, self.col

            # 识别关键字/符号
            token, new_pos, new_line, new_col = self.key_symbol_module.recognize(
                self.source_code, self.pos, self.line, self.col
            )
            if token:
                self.result_handler.add_token(token)
                self.pos, self.line, self.col = new_pos, new_line, new_col
                continue

            # 识别常量/标识符（处理非法标识符）
            try:
                token, new_pos, new_line, new_col = self.const_id_module.recognize(
                    self.source_code, self.pos, self.line, self.col
                )
                # 若识别到非法标识符，手动创建Token
                if not token and start_pos != new_pos:
                    illegal_str = self.source_code[start_pos:new_pos]
                    illegal_token = Token("非法标识符", illegal_str, start_line, start_col)
                    self.result_handler.add_token(illegal_token)
                    self.pos, self.line, self.col = new_pos, new_line, new_col
                    continue
                elif token:
                    self.result_handler.add_token(token)
                    self.pos, self.line, self.col = new_pos, new_line, new_col
                    continue
            except SyntaxError:
                pass

            # 处理未识别的非法序列
            illegal_end_pos = self.pos
            while (illegal_end_pos < len(self.source_code) and
                   self.source_code[illegal_end_pos] not in self.const_id_module.DELIMITERS):
                illegal_end_pos += 1
            illegal_str = self.source_code[self.pos:illegal_end_pos]
            if illegal_str:
                self.result_handler.record_error("非法字符", f"未识别：'{illegal_str}'", start_line, start_col)
                self.pos = illegal_end_pos
                self.col = start_col + (illegal_end_pos - start_pos)
            else:
                self.pos += 1
                self.col += 1
        self.result_handler.final_output()


# 测试代码
if __name__ == "__main__":
    lexer = MainController()
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
        student sts[2] = {
        {"Li ping",5,18,145.0}
        ,{"Wang ming",6,18,150.0}};

        if(sts[1].score < 140) 
        flag = -1;
        else flag=1;
        printf("%d", flag);
    """
    lexer.load_source(input_type="string", source_str=test_code)
    lexer.run_lexical_analysis()