import functools
import astor


@functools.singledispatch
def to_ast(x):
    """
    Convert Python object to an astroid AST.
    """

    try:
        conv = astor.codetoast
    except AttributeError:
        conv = astor.code_to_ast
    return conv(x)