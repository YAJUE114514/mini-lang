# builtins.py
from types import MappingProxyType
from functools import wraps

from interpreter.parser import Quot


def stack_args(num_args):
    """Decorator to check stack has enough arguments for a function"""

    def decorator(func):
        @wraps(func)
        def wrapper(runtime):
            stack = runtime.stack
            if len(stack) < num_args:
                from interpreter.evaluation import RunTimeError
                raise RunTimeError(f'Expected {num_args} items on stack but got {len(stack)}')
            return func(runtime)

        return wrapper

    return decorator


# Now you can decorate your functions
@stack_args(2)
def stack_plus(runtime):
    stack = runtime.stack
    a = stack.pop()
    b = stack.pop()
    stack.append(b + a)


@stack_args(2)
def stack_minus(runtime):
    stack = runtime.stack
    a = stack.pop()
    b = stack.pop()
    stack.append(b - a)


@stack_args(1)
def dup(runtime):
    stack = runtime.stack
    a = stack.pop()
    stack.append(a)
    stack.append(a)


@stack_args(1)
def run_quot(runtime):
    stack = runtime.stack
    quot = stack.pop()
    if not isinstance(quot, Quot):
        raise TypeError(f'Expected quotation but got {type(quot)}')
    expr = quot.expr
    runtime.visit_expr(expr)


@stack_args(0)
def print_stack(runtime):
    stack = runtime.stack
    print(stack)


@stack_args(1)
def print_top(runtime):
    stack = runtime.stack
    print(stack[-1])


BUILTIN_SCOPE = MappingProxyType({
    '+': stack_plus,
    '-': stack_minus,
    'dup': dup,
    '\\': run_quot,
})
