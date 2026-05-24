#!/usr/bin/env python3
"""C-lang → x86-64 GAS Assembly Compiler

Usage:
    python main.py <source.c> [-o output.asm] [--debug]   # 编译
    python main.py <source.c> --tree                       # 语法树分析
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'syntax_analyzer'))

from lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError
from codegen import CodeGenerator
from compiler import run_syntax_analysis


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python main.py <source.c> [-o output.asm] [--debug]")
        print("       python main.py <source.c> --tree")
        sys.exit(1)

    source_file = args[0]
    output_file = None
    debug = False
    show_tree = False

    i = 1
    while i < len(args):
        if args[i] == '-o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == '--debug':
            debug = True
            i += 1
        elif args[i] == '--tree':
            show_tree = True
            i += 1
        else:
            i += 1

    with open(source_file, 'r') as f:
        source = f.read()

    if show_tree:
        # 树模式：使用 syntax_analyzer 的词法 + LL(1) + 语义分析
        print("=" * 50)
        print("【syntax_analyzer】词法 + LL(1) 语法 + 语义分析")
        print("=" * 50)
        try:
            run_syntax_analysis(source)
        except Exception as e:
            print(f"  (语法分析器异常: {e})")
        return  # 树模式不生成汇编

    # 编译模式
    # Phase 1: Lexical analysis
    if debug:
        print("=== Phase 1: Lexical Analysis ===")
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
    except LexerError as e:
        print(f"Lexer error: {e}", file=sys.stderr)
        sys.exit(1)

    if debug:
        for tok in tokens:
            print(f"  {tok}")

    # Phase 2: Syntax analysis
    if debug:
        print("=== Phase 2: Syntax Analysis ===")
    try:
        parser = Parser(tokens)
        ast = parser.parse_program()
    except ParserError as e:
        print(f"Parser error: {e}", file=sys.stderr)
        sys.exit(1)

    if debug:
        print(f"  AST: {ast}")

    # Phase 3: Semantic analysis + intermediate code
    if debug:
        print("=== Phase 3: Semantic Analysis & TAC ===")
    try:
        analyzer = SemanticAnalyzer()
        ir = analyzer.analyze(ast)
    except SemanticError as e:
        print(f"Semantic error: {e}", file=sys.stderr)
        sys.exit(1)

    if debug:
        for fname, finfo in ir['functions'].items():
            print(f"  Function: {fname}")
            for instr in finfo['tac']:
                print(f"    {instr}")

    # Phase 4: Code generation
    if debug:
        print("=== Phase 4: Code Generation ===")
    codegen = CodeGenerator(ir)
    asm_code = codegen.generate()

    with open(output_file, 'w') as f:
        f.write(asm_code)

    print(f"Assembly written to {output_file}")

    if debug:
        print("=== Generated Assembly ===")
        print(asm_code)


if __name__ == '__main__':
    main()
