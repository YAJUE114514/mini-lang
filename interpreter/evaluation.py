# evaluation.py
import time

from interpreter.parser import ASTNode, Program, Decl, Expr, Literal, Identifier, Quot, List
from interpreter.builtins import BUILTIN_SCOPE


class RunTimeError(Exception):
    pass

class RunTime:
    """
    runtime for stack-based language interpreter
    """
    def __init__(self, parent: 'RunTime' = None):
        self.stack = []
        self.scope = {}
        self.builtin_scope = BUILTIN_SCOPE
        self.parent = parent
        self.recursion_depth = 0
        self.max_recursion_depth = 100

    def evaluate(self, node: ASTNode):
        node.accept(self)
        return self.stack

    def visit_program(self, program: Program):
        for stmt in program.statements:
            stmt.accept(self)

    def visit_decl(self, decl: Decl):
        ident_name = decl.word.name
        expr = decl.expr
        self.scope[ident_name] = expr

    def visit_expr(self, expr: Expr):
        for atom in expr.atoms:
            atom.accept(self)

    def visit_literal(self, literal: Literal):
        self.stack.append(literal.content)

    def visit_identifier(self, identifier: Identifier):
        if self.recursion_depth >= self.max_recursion_depth:
            self.recursion_depth = 0
            raise RunTimeError("Maximum recursion depth reached")

        self.recursion_depth += 1
        name = identifier.name
        if name in self.scope:
            expr = self.scope[name]
            expr.accept(self)
            self.recursion_depth -= 1
        elif name in self.builtin_scope:
            func = self.builtin_scope[name]
            func(self)
            self.recursion_depth -= 1
        else:
            cur_runtime = self
            while cur_runtime.parent:
                cur_runtime = cur_runtime.parent
                if name in cur_runtime.scope:
                    expr = cur_runtime.scope[name]
                    expr.accept(self)
                    self.recursion_depth -= 1
                    return
            raise RunTimeError(f"Unknown identifier {name}")

    def visit_quot(self, quot: Quot):
        self.stack.append(quot)

    def visit_list(self, lst: List):
        sub_runtime = RunTime(parent=self)
        sub_runtime.evaluate(lst.items)
        result = sub_runtime.stack
        self.stack.append(result)

    def generic_visit(self, node: ASTNode):
        pass

#!/usr/bin/env python3

def repl() -> None:
    import sys
    from interpreter.lexer import Lexer
    from interpreter.parser import Parser
    lexer = Lexer()
    parser = Parser()
    runtime = RunTime()

    print("Mini-lang 0.1.0  (type 'exit' or Ctrl-D to quit)")
    while True:
        try:
            source = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):         # Ctrl-C / Ctrl-D
            print("\nbye")
            break

        if not source:
            continue

        try:
            tokens = lexer.parse(source)
            ast    = parser.parse(tokens)
            runtime.evaluate(ast)
        except Exception as exc:
            print(f"{exc.__class__.__name__}: {exc}", file=sys.stderr)
            time.sleep(0.5)

if __name__ == "__main__":
    repl()