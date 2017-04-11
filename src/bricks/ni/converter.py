import ast
import collections
import copy
import io
import sys

import astor
from lazyutils import lazy

from bricks.ni.to_ast import to_ast


class FunctionCallTransform:
    def __init__(self, to_name):
        self.to_name = to_name

    def visit(self, transpiler, node):
        node = copy.deepcopy(node)
        node.func.id = self.to_name
        transpiler.visit(node)


def get_default_transforms():
    return {
        'builtins.print': FunctionCallTransform('console.log')
    }


class Scope(collections.MutableMapping):
    """
    An hierarchical dictionary
    """

    def __init__(self, data=None):
        self._data = [{}]
        self._data[0].update(data or {})

    def __getitem__(self, key):
        for D in reversed(self._data):
            try:
                return D[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._data[-1][key] = value

    def __delitem__(self, key):
        raise KeyError('cannot delete keys on Scope dictionaries')

    def __iter__(self):
        used = set()
        for D in reversed(self._data):
            for key in D:
                if key not in used:
                    used.add(key)
                    yield key

    def __len__(self):
        return sum(1 for _ in self)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self))

    def push_scope(self, data=None):
        """
        Create a new scope layer.

        Can pre-populate it with a dictionary of data.
        """

        self._data.append({})
        self._data[-1].update(data or {})

    def pop_scope(self):
        """
        Remove the last scope level and return the corresponding dictionary.
        """
        return self._data.pop()


class Transpiler:
    @lazy
    def file(self):
        raise RuntimeError('cannot be accessed outside the write method.')

    def __init__(self, node, dependencies=None, transforms=None):
        self.node = node
        self.indent_level = 0
        self.indent = ''
        self.scope = Scope()
        self.line_ended = False
        self.dependencies = set() if dependencies is None else dependencies
        self.transforms = transforms or get_default_transforms()

    def startline(self, st=''):
        self.file.write(self.indent + st)

    def endline(self, st=';'):
        self.write(st + '\n')
        self.line_ended = True

    def writeln(self, st=''):
        self.file.write(self.indent + st + '\n')

    def indent_up(self):
        self.indent_level += 1
        self.indent = '    ' * self.indent_level

    def indent_down(self):
        self.indent_level -= 1
        self.indent = '    ' * self.indent_level

    def error(self, msg):
        raise ValueError(msg)

    def write(self, value=''):
        self.file.write(value)

    def visit(self, node):
        if type(node) in (list, str, type(None), ast.Store, ast.Load):
            return

        if isinstance(node, (int, str)):
            self.write(str(node))
            return

        name = node.__class__.__name__
        try:
            walker = getattr(self, 'visit_' + name)
        except AttributeError:
            print()
            print('node:', name, file=sys.stderr)
            print('data:', node.__dict__, file=sys.stderr)
            astor.dump(node)
            raise NotImplementedError('node type not supported: %s' % name)
        walker(node)

    def local_var(self, name):
        return None

    def global_var(self, name):
        return None


class CClassTranspiler(Transpiler):
    pass


class CTranspiler(CClassTranspiler):
    pass


def extract_func_args(node):
    """
    Extract argument nodes from a Call element.
    """

    return node.args


class JsTranspiler(CClassTranspiler):
    def visit_body(self, L, indent=True):
        if indent:
            self.indent_up()

        for obj in L:
            self.line_ended = False
            self.visit(obj)
            if not self.line_ended:
                self.endline()

        if indent:
            self.indent_down()

    def visit_args(self, args):
        stop = len(args) - 1
        for i, elem in enumerate(args):
            self.visit(elem)
            if i != stop:
                self.write(', ')

    #
    # Function related
    #
    def visit_FunctionDef(self, node):
        # Consistency checks
        if node.decorator_list:
            self.error('function decorators are not supported in JS')

        # Write header
        self.scope.push_scope()
        self.write('function ' + node.name)
        self.visit(node.args)
        self.write(' {\n')

        # Body
        self.visit_body(node.body)

        # Finish
        self.scope.pop_scope()
        self.startline()
        self.endline('}')
        self.scope[node.name] = self.global_var(node.name)

    def visit_Lambda(self, node):
        self.write('function')
        self.visit(node.args)
        self.write('{return ')
        self.visit(node.body)
        self.write('}')

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name in self.transforms:
                self.transforms[name].visit(self, node)
                return

        self.visit(node.func)
        self.write('(')
        stop = len(node.args) - 1
        for i, arg in enumerate(node.args):
            self.visit(arg)
            if i != stop:
                self.write(', ')
        self.write(')')

        # We add the function into dependencies set if it was not defined in
        # any previous scope
        if node.func.id not in self.scope:
            self.dependencies.add(node.func.id)

    def visit_arg(self, node):
        self.write(node.arg)

    def visit_arguments(self, node):
        if node.vararg or node.kwonlyargs or node.kw_defaults or \
                node.kwarg or node.defaults:
            self.error('only support simple Python function signatures.')
        self.write('(')
        self.visit_args(node.args)
        self.write(')')

    def visit_Return(self, node):
        self.startline('return ')
        self.visit(node.value)
        self.endline()

    #
    # Assignments
    #
    def visit_Assign(self, node):
        if len(node.targets) == 1:
            name = node.targets[0]
            if name.id not in self.scope:
                self.startline('var ')
                self.scope[name.id] = self.local_var(name.id)
            else:
                self.startline()
            self.visit(name)
            self.write(' = ')
            self.visit(node.value)
            self.endline()
        else:
            raise NotImplementedError

    def visit_AugAssign(self, node):
        self.startline()
        self.visit(node.target)
        self.write(' ')
        self.visit(astor.get_anyop(node.op))
        self.write('= ')
        self.visit(node.value)
        self.endline()

    #
    # Operators
    #
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.write(' %s ' % astor.get_anyop(node.op))
        self.visit(node.right)

    def visit_Compare(self, node):
        self.visit(node.left)
        for op, right in zip(node.ops, node.comparators):
            self.write(' %s ' % astor.get_anyop(op))
            self.visit(right)

    #
    # Loops
    #
    def visit_While(self, node):
        if node.orelse:
            self.error('else clause of while node is not supported')
        self.startline('while (')
        self.visit(node.test)
        self.write(') {\n')
        self.visit_body(node.body)
        self.startline()
        self.endline('}')

    def visit_For(self, node):
        if node.iter.func.id == 'range':
            self.visit_For_range(node)
        else:
            raise NotImplementedError

    def visit_For_range(self, node):
        target = node.target.id
        if target not in self.scope:
            self.scope[target] = self.local_var(target)

        range_args = extract_func_args(node.iter)
        self.startline('for (%s = ' % target)
        if len(range_args) == 0:
            self.error('range has no arguments')
        elif len(range_args) == 1:
            start, end, inc = 0, range_args[0], '%s++' % target
        elif len(range_args) == 2:
            start, end = range_args[0]
            inc = '%s++' % target
        elif len(range_args) == 3:
            start, end, step = range_args
            inc = '%s += %s' % (target, step)
        else:
            self.error('range accepts up to 3 parameters.')

        self.visit(start)
        self.write('; %s < ' % target)
        self.visit(end)
        self.write('; %s)  {\n' % inc)
        self.visit_body(node.body)
        self.endline('}')

    #
    # Conditionals
    #
    def visit_If(self, node, start=True):
        if start:
            self.startline('if (')
        else:
            self.write('if (')
        self.visit(node.test)
        self.write(') {\n')
        self.visit_body(node.body)
        self.startline()
        self.endline('}')

        # Treat the else or else if clauses
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self.startline('else ')
                self.visit_If(node.orelse[0], False)
            else:
                self.startline('else {\n')
                self.visit_body(node.orelse)
                self.startline()
                self.endline('}')

    #
    # Expressions
    #
    def visit_Expr(self, node):
        self.startline()
        self.visit(node.value)
        self.endline()

    def visit_Pass(self, node):
        self.startline('null')
        self.endline()

    #
    # Primitives
    #
    def visit_Name(self, node):
        self.write(node.id)

    def visit_Num(self, node):
        self.write(str(node.n))

    def visit_Str(self, node):
        self.write(repr(node.s))

    def visit_List(self, node):
        self.write('[')
        self.visit_args(node.elts)
        self.write(']')

    def visit_Dict(self, node):
        self.write('{')
        stop = len(node.keys) - 1
        for i, (k, v) in enumerate(zip(node.keys, node.values)):
            self.visit(k)
            self.write(': ')
            self.visit(v)
            if i != stop:
                self.write(', ')
        self.write('}')

    def visit_NameConstant(self, node):
        value = node.value
        if value is True:
            self.write('true')
        elif value is False:
            self.write('false')
        elif value is None:
            self.write('null')
        else:
            self.error('javascript has no %s constant' % value)

    #
    # Public API and dumpers
    #
    def transpile(self):
        """
        Convert Python AST to JS source.
        """

        file = io.StringIO()
        self.dump(file)
        return file.getvalue()

    def dump(self, file):
        """
        Dump python ast to file.
        """

        self.file = file or sys.stdout
        self.visit(self.node)


def jsdump(pyobj, file=None, **kwargs):
    """
    Dumps JS code in the given file object.

    If no file object is given, dumps to sys.stdout
    """

    transpiler = JsTranspiler(to_ast(pyobj), **kwargs)
    transpiler.dump(file or sys.stdout)


def jstranspile(pyobj, **kwargs):
    """
    Converts python object to Javascript source code.
    """

    transpiler = JsTranspiler(to_ast(pyobj), **kwargs)
    return transpiler.transpile()


def cdump(pyobj, file=None, **kwargs):
    """
    Dumps C code in the given file object.

    If no file object is given, dumps to sys.stdout
    """

    transpiler = CTranspiler(to_ast(pyobj), **kwargs)
    transpiler.dump(file or sys.stdout)


def ctranspile(pyobj, **kwargs):
    """
    Transpile python code or object to C source.
    """

    transpiler = CTranspiler(to_ast(pyobj), **kwargs)
    return transpiler.transpile()


def dump(obj, lang, file=None, **kwargs):
    """
    Dump content of object in file as source code for the given language.
    """

    if lang in ('js', 'javascript'):
        return jsdump(obj, file=file, **kwargs)
    elif lang in ('c'):
        return cdump(obj, file=file, **kwargs)
    else:
        raise ValueError('language not supported: %r' % lang)


def transpile(obj, lang, file=None, **kwargs):
    """
    Transpile python source/object into the choosen language.

    Supported languages are JS, C.
    """

    if lang in ('js', 'javascript'):
        return jstranspile(obj, file=file, **kwargs)
    elif lang in ('c'):
        return ctranspile(obj, file=file, **kwargs)
    else:
        raise ValueError('language not supported: %r' % lang)



class VarType:
    name = None


class NamedVarType(VarType):
    def __init__(self, name):
        self.name = name


#
# Still testing...!
#
from math import sqrt


def entropy(data: 'double[]', N: int) -> 'double':
    S = 0.0
    for i in range(N):
        x = data[i]
        if x == 0.0:
            return x
        else:
            S += - x * log(x)
    return S


jsdump(entropy)


def func(x, y):
    z = sqrt(x + 1e10)
    L = [1, 2, 3]
    x = {'sdfs': 2}
    z += x

    12
    while True:
        if x == 2:
            print(2)
        elif x == 3 == 3:
            print(4)
        else:
            x = lambda x: 2 ** 2
    return z + y


D = set()
jsdump(func, dependencies=D)
print(D)


def jsfunc(func):
    """
    Marks a Python function as a js-compatible one
    """

    if not hasattr(func, '__jssource__'):
        func.__jssource__ = jstranspile(func)

    return func
