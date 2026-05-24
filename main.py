#!/usr/bin/env python3
"""C-lang → x86-64 NASM Assembly Compiler

Usage: python main.py <source.c> [-o output.asm] [--debug]
"""

import sys
import os

from lexer import Lexer, LexerError
from parser import Parser, ParserError
from semantic import SemanticAnalyzer, SemanticError
from codegen import CodeGenerator


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python main.py <source.c> [-o output.asm] [--debug]")
        sys.exit(1)

    source_file = args[0]
    output_file = None
    debug = False

    i = 1
    while i < len(args):
        if args[i] == '-o' and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == '--debug':
            debug = True
            i += 1
        else:
            i += 1

    if output_file is None:
        base = os.path.splitext(source_file)[0]
        output_file = base + '.asm'

    with open(source_file, 'r') as f:
        source = f.read()

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
